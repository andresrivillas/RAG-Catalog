from typing import List, Optional

from ...entities.commercial_intent import CommercialIntent
from ...entities.commercial_proposal import CommercialProposal, ProposalItem
from ...services.budget_plan import BudgetPlan
from .proposal_score_card import CriterionResult, ProposalScoreCard

ROLE_HINT_KEYWORDS = {
    "escritura": ["lapiz", "boligrafo", "bolígrafo", "resaltador", "pluma", "portaminas"],
    "bolsos": ["bolsa", "mochila", "cartera", "estuche"],
    "hogar": ["taza", "mug", "termo", "vaso", "plat", "copa", "toalla"],
    "tecnologia": ["usb", "cargador", "auricular", "altavoz", "speaker", "power bank"],
    "oficina": ["libreta", "cuaderno", "carpeta", "agenda", "notas"],
    "viaje": ["paraguas", "maleta", "neceser", "viaje"],
}
ECO_KEYWORDS = ["eco", "ecologico", "ecológico", "sostenible", "rpet", "recicl", "bambu", "bambú"]
PERSONALIZATION_KEYWORDS = [
    "logo", "grabado", "personaliz", "marca", "tampografia", "tampografía", "sublimacion", "sublimación",
]
PREMIUM_MATERIALS = [
    "cuero", "leather", "acero", "metal", "madera", "bambu", "bambú",
    "aluminio", "vidrio", "cristal", "silicona", "premium",
]
UTILITY_KEYWORDS = [
    "reusable", "plegable", "multiusos", "portatil", "portátil", "carga",
    "usb", "inalambrico", "inalámbrico", "termost", "termo", "impermeable",
]


class BaseCriterion:
    name: str = ""
    weight_key: str = ""

    def evaluate(
        self,
        proposal: CommercialProposal,
        intent: Optional[CommercialIntent],
        plan: Optional[BudgetPlan],
    ) -> CriterionResult:
        raise NotImplementedError

    def _category(self, item: ProposalItem) -> str:
        text = (item.name or "").lower()
        for category, keywords in ROLE_HINT_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return category
        return "otros"

    def _text(self, item: ProposalItem) -> str:
        return f"{item.name or ''} {item.selection_reason or ''}".lower()


class BudgetEfficiencyCriterion(BaseCriterion):
    name = "Budget Efficiency"
    weight_key = "budget"

    def evaluate(self, proposal, intent, plan):
        if plan is None or plan.spendable_budget <= 0:
            score = 50.0
            reason = "Sin plan de presupuesto; se asume eficiencia neutral."
        else:
            used = proposal.total_cost.amount
            ceiling = plan.spendable_budget
            if used <= 0:
                score = 0.0
                reason = "Propuesta sin costo calculado."
            elif used > ceiling:
                over = (used - ceiling) / ceiling
                score = max(0.0, 60.0 - over * 100)
                reason = (
                    f"Supera el presupuesto utilizable en {over*100:.0f}%; "
                    f"usa {used:,.0f} de {ceiling:,.0f} COP."
                )
            else:
                ratio = used / ceiling
                target_min, target_max = plan.utilization_target
                if ratio >= target_min:
                    # Dentro o cerca del objetivo: puntuacion alta.
                    score = 80.0 + min(ratio, 1.0) * 20.0
                elif ratio >= 0.70:
                    # Cercano pero por debajo del objetivo: penalizacion moderada.
                    score = 55.0 + (ratio - 0.70) / (target_min - 0.70) * 25.0
                else:
                    # Subutilizacion grave (30-50%): penalizacion fuerte.
                    score = max(0.0, ratio / 0.70 * 55.0)
                reason = (
                    f"Utiliza {ratio*100:.0f}% del presupuesto "
                    f"({used:,.0f} de {ceiling:,.0f} COP); "
                    f"objetivo {target_min*100:.0f}-{target_max*100:.0f}%."
                )
        return CriterionResult(self.name, score, reason)


class CommercialValueCriterion(BaseCriterion):
    name = "Commercial Value"
    weight_key = "commercial"

    def evaluate(self, proposal, intent, plan):
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        total = 0.0
        notes = []
        for item in proposal.items:
            val = 50.0
            if item.decision_trace is not None:
                val = max(0.0, min(100.0, item.decision_trace.commercial_score))
            total += val
            if "alto valor percibido" in (item.selection_reason or "").lower():
                notes.append(f"{item.name} (alto valor percibido)")
        avg = total / len(proposal.items)
        reason = (
            f"Valor comercial promedio {avg:.0f}/100 de {len(proposal.items)} productos."
            + (f" Destacan: {', '.join(notes)}." if notes else "")
        )
        return CriterionResult(self.name, avg, reason)


class KitCoherenceCriterion(BaseCriterion):
    name = "Kit Coherence"
    weight_key = "coherence"

    def evaluate(self, proposal, intent, plan):
        items = proposal.items
        if len(items) < 2:
            return CriterionResult(
                self.name, 20.0, "Kit de un solo producto; coherencia muy baja."
            )
        cats = [self._category(it) for it in items]
        distinct = set(cats)
        repeated = len(cats) - len(distinct)
        base = 100.0 - repeated * 30.0
        roles = {it.role for it in items if it.role}
        has_core = "CORE" in roles
        has_util = "UTILITY" in roles
        if not has_core:
            base -= 20.0
        if not has_util:
            base -= 10.0
        reason = (
            f"{len(items)} productos en {len(distinct)} categorias; "
            f"{repeated} categoria(s) repetida(s); "
            + ("incluye producto central (CORE)." if has_core else "falta producto central (CORE).")
            + (" Incluye utilidad (UTILITY)." if has_util else " Falta utilidad (UTILITY).")
        )
        return CriterionResult(self.name, max(0.0, min(100.0, base)), reason)


class ProductDiversityCriterion(BaseCriterion):
    name = "Product Diversity"
    weight_key = "diversity"

    def evaluate(self, proposal, intent, plan):
        n = len(proposal.items)
        score = min(n, 5) / 5 * 100.0
        reason = f"{n} productos distintos en el kit (max 5 evaluados)."
        return CriterionResult(self.name, score, reason)


class CategoryDiversityCriterion(BaseCriterion):
    name = "Category Diversity"
    weight_key = "category_diversity"

    def evaluate(self, proposal, intent, plan):
        cats = {self._category(it) for it in proposal.items}
        cats.discard("otros")
        score = min(len(cats), 4) / 4 * 100.0
        reason = f"{len(cats)} categorias distintas: {', '.join(sorted(cats)) or 'ninguna clasificable'}."
        return CriterionResult(self.name, score, reason)


class PracticalUtilityCriterion(BaseCriterion):
    name = "Practical Utility"
    weight_key = "utility"

    def evaluate(self, proposal, intent, plan):
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        hits = 0
        for item in proposal.items:
            if any(k in self._text(item) for k in UTILITY_KEYWORDS) or item.role in (
                "UTILITY", "CORE",
            ):
                hits += 1
        score = hits / len(proposal.items) * 100.0
        reason = f"{hits} de {len(proposal.items)} productos con utilidad practica diaria."
        return CriterionResult(self.name, score, reason)


class BrandVisibilityCriterion(BaseCriterion):
    name = "Brand Visibility"
    weight_key = "brand"

    def evaluate(self, proposal, intent, plan):
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        hits = 0
        for item in proposal.items:
            if any(k in self._text(item) for k in PERSONALIZATION_KEYWORDS) or item.role == "PROMOTIONAL":
                hits += 1
        score = hits / len(proposal.items) * 100.0
        reason = f"{hits} de {len(proposal.items)} productos refuerzan la marca (logo/personalizacion)."
        return CriterionResult(self.name, score, reason)


class PremiumPerceptionCriterion(BaseCriterion):
    name = "Premium Perception"
    weight_key = "premium"

    def evaluate(self, proposal, intent, plan):
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        total = 0.0
        count = 0
        for item in proposal.items:
            if item.role == "PREMIUM":
                total += 100.0
                count += 1
            elif any(m in self._text(item) for m in PREMIUM_MATERIALS):
                total += 75.0
                count += 1
            elif (item.decision_trace is not None
                  and getattr(item.decision_trace, "commercial_score", 0) >= 70):
                total += 60.0
                count += 1
        score = total / len(proposal.items)
        reason = f"{count} de {len(proposal.items)} productos con percepcion premium."
        return CriterionResult(self.name, score, reason)


class SustainabilityCriterion(BaseCriterion):
    name = "Sustainability"
    weight_key = "eco"

    def evaluate(self, proposal, intent, plan):
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        hits = 0
        for item in proposal.items:
            if any(k in self._text(item) for k in ECO_KEYWORDS):
                hits += 1
        score = hits / len(proposal.items) * 100.0
        reason = f"{hits} de {len(proposal.items)} productos con atributos eco/sostenibles."
        return CriterionResult(self.name, score, reason)


class PersonalizationPotentialCriterion(BaseCriterion):
    name = "Personalization Potential"
    weight_key = "personalization"

    def evaluate(self, proposal, intent, plan):
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        hits = 0
        for item in proposal.items:
            if any(k in self._text(item) for k in PERSONALIZATION_KEYWORDS):
                hits += 1
        score = hits / len(proposal.items) * 100.0
        reason = f"{hits} de {len(proposal.items)} productos personalizables (logo/grabado)."
        return CriterionResult(self.name, score, reason)


class OccasionFitCriterion(BaseCriterion):
    name = "Occasion Fit"
    weight_key = "occasion"

    def evaluate(self, proposal, intent, plan):
        if intent is None or not intent.occasion:
            return CriterionResult(
                self.name, 50.0, "Sin ocasion especificada; ajuste neutral."
            )
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        total = 0.0
        for item in proposal.items:
            if item.decision_trace is not None:
                total += item.decision_trace.occasion_score * 100.0
            elif proposal.occasion and proposal.occasion == intent.occasion:
                total += 60.0
            else:
                total += 40.0
        score = total / len(proposal.items)
        reason = f"Ajuste a ocasion '{intent.occasion}' promedio {score:.0f}/100."
        return CriterionResult(self.name, score, reason)


class AudienceFitCriterion(BaseCriterion):
    name = "Audience Fit"
    weight_key = "audience"

    def evaluate(self, proposal, intent, plan):
        if intent is None or not intent.target_audience:
            return CriterionResult(
                self.name, 50.0, "Sin publico especificado; ajuste neutral."
            )
        segments = set(intent.segment_tags or [intent.target_audience])
        hits = 0
        matched_names = []
        for item in proposal.items:
            signals = (
                [t.lower() for t in (item.audience_tags or [])]
                + [t.lower() for t in (item.commercial_tags or [])]
                + (item.selection_reason or "").lower().split()
            )
            if any(seg.lower() in signals for seg in segments):
                hits += 1
                matched_names.append(item.name)
        score = hits / len(proposal.items) * 100.0
        reason = (
            f"Ajuste a publico '{intent.target_audience}': "
            f"{hits} de {len(proposal.items)} productos alineados"
            + (f" ({', '.join(matched_names[:3])})." if matched_names else ".")
        )
        return CriterionResult(self.name, score, reason)


class ProposalBalanceCriterion(BaseCriterion):
    name = "Proposal Balance"
    weight_key = "balance"

    def evaluate(self, proposal, intent, plan):
        items = proposal.items
        if not items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        if plan is None or plan.quantity <= 0:
            return CriterionResult(self.name, 50.0, "Sin cantidad; balance neutral.")
        prices = [it.unit_price.amount for it in items if it.unit_price.amount > 0]
        if not prices:
            return CriterionResult(self.name, 0.0, "Sin precios validos.")
        spread = (max(prices) - min(prices)) / max(prices)
        balanced = 1.0 - abs(spread - 0.5)
        score = max(0.0, min(1.0, balanced)) * 100.0
        reason = (
            f"Rango de precios {min(prices):,.0f}-{max(prices):,.0f} COP; "
            f"equilibrio {score:.0f}/100 (ideal ~50% de diferencia)."
        )
        return CriterionResult(self.name, score, reason)


class IndustryFitCriterion(BaseCriterion):
    name = "Industry Fit"
    weight_key = "industry"

    def evaluate(self, proposal, intent, plan):
        if intent is None or not intent.industry:
            return CriterionResult(
                self.name, 50.0, "Sin industria especificada; ajuste neutral."
            )
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        from ..industry_knowledge import IndustryKnowledge

        ik = IndustryKnowledge()
        profile = ik.get(intent.industry)
        if profile is None:
            return CriterionResult(
                self.name, 50.0, "Industria no mapeada; ajuste neutral."
            )
        aligned = 0
        avoided = 0
        aligned_names = []
        for item in proposal.items:
            signals = (
                f"{item.name} {item.category} {item.materials}".lower()
            )
            if any(a in signals for a in profile.avoid):
                avoided += 1
            elif any(p in signals for p in profile.prefer):
                aligned += 1
                aligned_names.append(item.name)
        if avoided > 0 and aligned == 0:
            score = 10.0
        elif avoided > 0:
            score = 40.0
        elif aligned > 0:
            score = min(100.0, 60.0 + aligned / len(proposal.items) * 40.0)
        else:
            score = 50.0
        reason = (
            f"Ajuste a industria '{intent.industry}': "
            f"{aligned} productos alineados"
            + (f" ({', '.join(aligned_names[:3])})" if aligned_names else "")
            + (f"; {avoided} productos incompatibles." if avoided else ".")
        )
        return CriterionResult(self.name, score, reason)


class ComplementarityCriterion(BaseCriterion):
    name = "Complementarity"
    weight_key = "complementarity"

    def evaluate(self, proposal, intent, plan):
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        from ..complementarity import kit_complementarity

        products = []
        for item in proposal.items:
            from ...entities.product_knowledge import ProductKnowledge

            products.append(
                ProductKnowledge(
                    reference=item.reference,
                    name=item.name,
                    price=item.unit_price,
                    category=item.category,
                    description=item.name,
                )
            )
        score = kit_complementarity(products) * 100.0
        reason = (
            f"Complementariedad del kit: {score:.0f}/100 "
            f"(productos que se complementan en lugar de competir)."
        )
        return CriterionResult(self.name, score, reason)


ALL_CRITERIA = [
    BudgetEfficiencyCriterion,
    CommercialValueCriterion,
    KitCoherenceCriterion,
    ProductDiversityCriterion,
    CategoryDiversityCriterion,
    PracticalUtilityCriterion,
    BrandVisibilityCriterion,
    PremiumPerceptionCriterion,
    SustainabilityCriterion,
    PersonalizationPotentialCriterion,
    OccasionFitCriterion,
    AudienceFitCriterion,
    ProposalBalanceCriterion,
    IndustryFitCriterion,
    ComplementarityCriterion,
]
