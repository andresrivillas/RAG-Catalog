import html
import re
import unicodedata
from typing import List, Optional

from ...entities.commercial_intent import CommercialIntent
from ...entities.commercial_proposal import CommercialProposal, ProposalItem
from ...services.budget_plan import BudgetPlan
from ...services.material_reasoner import MATERIAL_FAMILIES, material_families
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

# Categorías comerciales canónicas (sin acentos, minúsculas).
CANONICAL_CATEGORIES = {
    "tecnologia", "oficina", "viaje", "hogar", "eco", "bebidas", "textiles",
    "herramientas", "maletines", "termos", "libretas", "escritura", "bolsos",
    "salud", "eventos", "deportes", "accesorios", "limpieza", "otros",
}

# Términos que indican texto sucio de menú, HTML o logística/inventario.
DIRTY_TERMS = {
    "html", "body", "href", "src", "script", "style", "div", "span", "nbsp",
    "class=", "id=", "http", "www", ".com", "inventario", "existencias",
    "bodega", "almacen", "almacén", "envio", "envío", "despacho",
    "transporte", "logistica", "logística", "unidades", "cantidad", "pedido",
    "entrega", "caja master", "caja máster", "disponible", "agotado", "stock",
    "menu", "menú", "categorias", "categorías", "ver todo", "ver todos",
    "subcategorias", "subcategorías", "volver", "seguir",
}

# Materiales comercialmente conocidos para regalos promocionales.
KNOWN_MATERIALS: set = set()
for _terms in MATERIAL_FAMILIES.values():
    KNOWN_MATERIALS.update(_terms)

# Separadores que sugieren múltiples categorías concatenadas.
CATEGORY_SPLIT_RE = re.compile(r"[,;/|>]+|\sy\s|\se\s")


def _normalize(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9\s]", " ", text.lower()).strip()


def _strip_html(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(clean)


def _contains_dirty(text: str) -> bool:
    norm = _normalize(text)
    return any(term in norm for term in DIRTY_TERMS)


def _looks_like_menu(text: str) -> bool:
    norm = _normalize(text)
    menu_hints = {"menu", "categorias", "ver todo", "ver todos", "subcategorias"}
    return any(hint in norm for hint in menu_hints)


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
            score = 0.0
        elif avoided > 0:
            score = 30.0
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


class CategoryQualityCriterion(BaseCriterion):
    name = "Category Quality"
    weight_key = "category_quality"

    def evaluate(self, proposal, intent, plan):
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        scores = []
        dirty = []
        multi = []
        unknown = []
        for item in proposal.items:
            raw = (item.category or "").strip()
            if not raw:
                scores.append(0.0)
                unknown.append(item.name)
                continue
            if len(raw) > 60 or _contains_dirty(raw) or _looks_like_menu(raw):
                scores.append(0.0)
                dirty.append(item.name)
                continue
            cleaned = _strip_html(raw)
            parts = [p.strip() for p in CATEGORY_SPLIT_RE.split(cleaned) if p.strip()]
            if len(parts) > 1:
                scores.append(20.0)
                multi.append(item.name)
                continue
            norm = _normalize(parts[0])
            if norm in CANONICAL_CATEGORIES:
                scores.append(100.0)
            else:
                scores.append(40.0)
                unknown.append(item.name)
        score = sum(scores) / len(scores) if scores else 0.0
        notes = []
        if dirty:
            notes.append(f"{len(dirty)} con texto sucio")
        if multi:
            notes.append(f"{len(multi)} con múltiples categorías")
        if unknown:
            notes.append(f"{len(unknown)} no canónicas")
        reason = (
            f"Categorías comerciales: {sum(1 for s in scores if s == 100.0)} de {len(scores)} limpias"
            + (f" ({', '.join(notes)})." if notes else ".")
        )
        return CriterionResult(self.name, score, reason)


class MaterialCleanlinessCriterion(BaseCriterion):
    name = "Material Cleanliness"
    weight_key = "material_cleanliness"

    def evaluate(self, proposal, intent, plan):
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        scores = []
        dirty = []
        unknown = []
        for item in proposal.items:
            raw = (item.materials or "").strip()
            if not raw:
                scores.append(50.0)
                continue
            if len(raw) > 100 or _contains_dirty(raw) or "<" in raw:
                scores.append(0.0)
                dirty.append(item.name)
                continue
            cleaned = _strip_html(raw)
            tokens = [t for t in re.split(r"[,;/|&\s]+", cleaned.lower()) if t and len(t) > 2]
            if not tokens:
                scores.append(50.0)
                continue
            known_count = 0
            for token in tokens:
                if token in KNOWN_MATERIALS or material_families(token):
                    known_count += 1
            ratio = known_count / len(tokens)
            if ratio >= 0.75:
                scores.append(100.0)
            elif ratio >= 0.5:
                scores.append(70.0)
            else:
                scores.append(30.0)
                unknown.append(item.name)
        score = sum(scores) / len(scores) if scores else 0.0
        reason = (
            f"Materiales limpios: {sum(1 for s in scores if s == 100.0)} de {len(scores)}"
            + (f" ({len(dirty)} sucios, {len(unknown)} desconocidos)." if dirty or unknown else ".")
        )
        return CriterionResult(self.name, score, reason)


class ModeCoherenceCriterion(BaseCriterion):
    name = "Mode Coherence"
    weight_key = "mode_coherence"

    def evaluate(self, proposal, intent, plan):
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        mode = (proposal.generation_mode or (intent.generation_mode if intent else "") or "balanced").lower()
        n = len(proposal.items)
        if mode == "premium":
            hits = sum(
                1
                for it in proposal.items
                if it.role == "PREMIUM"
                or any(m in self._text(it) for m in PREMIUM_MATERIALS)
                or it.perceived_value_level == "alto"
            )
            score = hits / n * 100.0
            reason = f"{hits} de {n} productos con apariencia premium (modo {mode})."
        elif mode == "eco":
            hits = sum(
                1
                for it in proposal.items
                if it.eco or any(k in self._text(it) for k in ECO_KEYWORDS)
            )
            score = hits / n * 100.0
            reason = f"{hits} de {n} productos con atributos eco/sostenibles (modo {mode})."
        elif mode == "budget":
            ceiling = plan.per_unit_ceiling if plan else 0.0
            if ceiling <= 0:
                score = 50.0
                reason = "Sin tope presupuestario; coherencia de modo budget neutral."
            else:
                hits = sum(1 for it in proposal.items if it.unit_price.amount <= ceiling * 0.6)
                score = hits / n * 100.0
                reason = f"{hits} de {n} productos bajo costo (<=60% del tope; modo {mode})."
        else:
            score = 70.0
            reason = f"Modo {mode}; coherencia balanceada sin penalización."
        return CriterionResult(self.name, score, reason)


class AvailabilityCriterion(BaseCriterion):
    name = "Availability"
    weight_key = "availability"

    def evaluate(self, proposal, intent, plan):
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        known = 0
        ok = 0
        short = []
        for item in proposal.items:
            availability = getattr(item, "availability", None)
            if availability is None:
                continue
            known += 1
            if availability >= item.quantity:
                ok += 1
            else:
                short.append(item.name)
        if known == 0:
            return CriterionResult(
                self.name, 50.0, "Disponibilidad desconocida; criterio neutral."
            )
        score = ok / known * 100.0
        reason = (
            f"Disponibilidad: {ok} de {known} productos con stock suficiente"
            + (f" ({', '.join(short[:3])} con faltante)." if short else ".")
        )
        return CriterionResult(self.name, score, reason)


class SelectionReasonQualityCriterion(BaseCriterion):
    name = "Selection Reason Quality"
    weight_key = "selection_reason_quality"

    def evaluate(self, proposal, intent, plan):
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        scores = []
        bad = []
        for item in proposal.items:
            reason = (item.selection_reason or "").strip()
            if not reason:
                scores.append(0.0)
                bad.append(item.name)
                continue
            if len(reason) > 300:
                scores.append(30.0)
                bad.append(item.name)
                continue
            if _contains_dirty(reason) or "<" in reason:
                scores.append(10.0)
                bad.append(item.name)
                continue
            scores.append(100.0)
        score = sum(scores) / len(scores) if scores else 0.0
        reason = (
            f"Justificaciones válidas: {sum(1 for s in scores if s == 100.0)} de {len(scores)}"
            + (f" ({len(bad)} deficientes)." if bad else ".")
        )
        return CriterionResult(self.name, score, reason)


class ConsistencyCriterion(BaseCriterion):
    name = "Consistency"
    weight_key = "consistency"

    def evaluate(self, proposal, intent, plan):
        items = proposal.items
        if not items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        industry = (intent.industry or "").lower() if intent else ""
        per_item = []
        for item in items:
            reason = (item.selection_reason or "").lower()
            score = 50.0
            if item.category and item.category.lower() in reason:
                score += 15.0
            if item.materials:
                mat_families = material_families(item.materials)
                if mat_families and any(m in reason for m in mat_families):
                    score += 15.0
            if industry and industry in reason:
                score += 15.0
            if item.role and item.role.lower() in reason:
                score += 5.0
            per_item.append(min(100.0, score))
        # Penalización por repeticiones de categoría o material.
        categories = [self._category(it) for it in items]
        materials = [item.materials.lower() if item.materials else None for item in items]
        repeated = 0
        for idx in range(len(items)):
            for jdx in range(idx + 1, len(items)):
                if categories[idx] == categories[jdx] and categories[idx] != "otros":
                    repeated += 1
                if materials[idx] and materials[idx] == materials[jdx]:
                    repeated += 1
        penalty = min(40.0, repeated * 10.0)
        score = max(0.0, sum(per_item) / len(per_item) - penalty)
        reason = (
            f"Coherencia interna del kit: {score:.0f}/100 "
            f"({repeated} repeticiones detectadas)."
        )
        return CriterionResult(self.name, score, reason)


class ExplainabilityCriterion(BaseCriterion):
    name = "Explainability"
    weight_key = "explainability"

    def evaluate(self, proposal, intent, plan):
        if not proposal.items:
            return CriterionResult(self.name, 0.0, "Sin productos.")
        industry = (intent.industry or "").lower() if intent else ""
        total = 0.0
        bad = []
        for item in proposal.items:
            reason = (item.selection_reason or "").strip()
            if not reason or len(reason) > 200 or _contains_dirty(reason):
                total += 0.0
                bad.append(item.name)
                continue
            # Base por tener una justificación clara y corta.
            score = 60.0
            # Bonus si menciona el rol.
            if item.role and item.role.lower() in reason.lower():
                score += 20.0
            # Bonus si menciona la industria o segmentos.
            if industry and industry in reason.lower():
                score += 20.0
            elif intent and intent.segment_tags and any(
                k in reason.lower() for k in intent.segment_tags
            ):
                score += 20.0
            total += min(100.0, score)
        score = total / len(proposal.items) if proposal.items else 0.0
        reason = (
            f"Justificaciones explicables: {sum(1 for it in proposal.items if (it.selection_reason or '').strip() and len(it.selection_reason) <= 200)} de {len(proposal.items)}"
            + (f" ({len(bad)} deficientes)." if bad else ".")
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
    CategoryQualityCriterion,
    MaterialCleanlinessCriterion,
    ModeCoherenceCriterion,
    AvailabilityCriterion,
    SelectionReasonQualityCriterion,
    ConsistencyCriterion,
    ExplainabilityCriterion,
]
