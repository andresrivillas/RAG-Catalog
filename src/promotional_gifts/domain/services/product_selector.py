from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from ..entities.commercial_intent import CommercialIntent
from ..entities.product_knowledge import ProductKnowledge
from ..services.budget_plan import BudgetPlan
from ..services.commercial_scorer import CommercialScorer
from ..services.complementarity import products_complement
from ..services.decision_trace import DecisionTrace
from ..services.generation_mode import GenerationMode, ModeProfile, get_profile
from ..services.industry_affinity_service import IndustryAffinityService
from ..services.industry_knowledge import IndustryKnowledge
from ..services.material_reasoner import material_families
from ..services.negative_filter import NegativeFilter
from ..services.occasion_matcher import OccasionMatcher
from ..services.reason_generator import generate as generate_reason

ECO_KEYWORDS = ["eco", "ecologico", "ecológico", "sostenible", "rpet", "recicl"]
PERSONALIZABLE_KEYWORDS = [
    "logo", "grabado", "personaliz", "marca", "tampografia", "tampografía",
]
PREMIUM_MATERIALS = [
    "cuero", "leather", "acero", "metal", "madera", "bambu", "bambú",
    "aluminio", "vidrio", "cristal", "silicona", "premium",
]


@dataclass
class ScoredProduct:
    product: ProductKnowledge
    similarity: float
    score: float
    trace: DecisionTrace = field(default_factory=DecisionTrace)


class ProductSelector:
    def __init__(
        self,
        occasion_matcher: OccasionMatcher,
        commercial_scorer: CommercialScorer,
        negative_filter: NegativeFilter,
        industry_knowledge: IndustryKnowledge = None,
        industry_affinity_service: IndustryAffinityService = None,
    ) -> None:
        self.occasion_matcher = occasion_matcher
        self.commercial_scorer = commercial_scorer
        self.negative_filter = negative_filter
        self.industry_knowledge = industry_knowledge or IndustryKnowledge()
        self.industry_affinity_service = industry_affinity_service or IndustryAffinityService(
            self.industry_knowledge
        )

    def select(
        self,
        candidates: List[Tuple[ProductKnowledge, float]],
        intent: CommercialIntent,
        plan: BudgetPlan,
        mode: GenerationMode = None,
        drop_restrictions: List[str] = None,
    ) -> List[ScoredProduct]:
        profile = get_profile(mode)
        drop = set(drop_restrictions or [])
        eligible: List[ScoredProduct] = []

        for product, similarity in candidates:
            trace = DecisionTrace(semantic_score=max(0.0, min(1.0, similarity)))

            if not self._valid_price(product):
                trace.reason = "Precio inválido o ausente; excluido."
                continue
            if self.negative_filter.is_excluded(product):
                trace.reason = "Categoría incompatible (filtro negativo)."
                continue
            if not self._passes_intent_filters(product, intent, plan, trace, drop):
                continue

            trace.occasion_score = self.occasion_matcher.score(intent, product)
            trace.commercial_score = self.commercial_scorer.score(intent, product)
            trace.budget_score = self._budget_utilization_score(product, plan, profile)
            trace.context_score = self._context_match_score(intent, product)
            trace.industry_score = self._industry_score(intent, product)
            trace.affinity_score = self.industry_affinity_service.affinity(product, intent)
            trace.availability_score = self._availability_score(product, intent, trace)
            if trace.availability_score == 0.0:
                trace.reason = "Stock insuficiente para la cantidad solicitada."
                continue

            trace.final_score = self._combine(trace, profile, product, plan, intent)
            trace.reason = generate_reason(product, intent, None, trace)
            eligible.append(ScoredProduct(product, similarity, trace.final_score, trace))

        eligible.sort(key=lambda sp: sp.score, reverse=True)
        return eligible

    def _product_signals(self, product: ProductKnowledge) -> str:
        return (
            f"{product.name} {product.description} {product.materials} "
            f"{product.category} {(product.subcategory or '')} "
            f"{' '.join(product.commercial_tags)} {' '.join(product.audience_tags)} "
            f"{' '.join(product.occasion_tags)} {product.benefits}".lower()
        )

    def _industry_score(
        self, intent: CommercialIntent, product: ProductKnowledge
    ) -> float:
        if not intent.industry:
            return 0.5
        return self.industry_knowledge.industry_score(
            intent.industry, self._product_signals(product)
        )

    def _context_match_score(
        self, intent: CommercialIntent, product: ProductKnowledge
    ) -> float:
        if not intent.commercial_context_tags:
            return 0.5
        product_signals = (
            [t.lower() for t in product.audience_tags]
            + [t.lower() for t in product.commercial_tags]
            + [t.lower() for t in product.occasion_tags]
            + [product.category.lower(), (product.subcategory or "").lower()]
        )
        text = " ".join(product_signals)
        if not text.strip():
            text = f"{product.name} {product.description} {product.materials}".lower()
        hits = 0
        for tag in intent.commercial_context_tags:
            if tag.lower() in text:
                hits += 1
        if not hits:
            return 0.3
        return min(1.0, 0.5 + hits * 0.25)

    def _valid_price(self, product: ProductKnowledge) -> bool:
        return product.price.amount > 0

    def _passes_intent_filters(
        self,
        product: ProductKnowledge,
        intent: CommercialIntent,
        plan: BudgetPlan,
        trace: DecisionTrace,
        drop: set = None,
    ) -> bool:
        drop = drop or set()
        # Sin techo de presupuesto (solicitud generica sin presupuesto): no
        # se excluye por precio; el kit se arma con lo disponible.
        if plan.per_unit_ceiling > 0 and product.price.amount > plan.per_unit_ceiling:
            trace.reason = "Supera el presupuesto por unidad."
            return False
        # Restriccion critica: industria. Si el producto pertenece a una
        # categoria explicitamente rechazada por la industria, se excluye
        # salvo que se haya relajado la restriccion (fallback inteligente).
        if intent.industry and "industry" not in drop:
            if self.industry_knowledge.is_avoided(
                intent.industry, self._product_signals(product)
            ):
                trace.reason = (
                    f"Categoria incompatible con la industria {intent.industry}."
                )
                return False
        if intent.eco and "eco" not in drop and not self._is_eco(product):
            trace.reason = "No cumple restricción ecológica."
            return False
        if (
            intent.personalizable
            and "personalizable" not in drop
            and not self._is_personalizable(product)
        ):
            trace.reason = "No es personalizable."
            return False
        return True

    def _budget_utilization_score(
        self, product: ProductKnowledge, plan: BudgetPlan, profile: ModeProfile
    ) -> float:
        if plan.per_unit_ceiling <= 0:
            return 0.0
        ratio = product.price.amount / plan.per_unit_ceiling
        target_mid = profile.utilization_target_mid
        tolerance = 0.35
        distance = abs(ratio - target_mid)
        return max(0.0, 1.0 - distance / tolerance)

    def _availability_score(
        self,
        product: ProductKnowledge,
        intent: CommercialIntent,
        trace: DecisionTrace,
    ) -> float:
        if product.availability is None:
            return 0.5
        quantity = intent.quantity or 0
        if quantity <= 0:
            # Sin cantidad explicita: cualquier stock positivo es neutral-alto.
            return 1.0 if product.availability > 0 else 0.0
        return 1.0 if product.availability >= quantity else 0.0

    def _combine(
        self,
        trace: DecisionTrace,
        profile: ModeProfile,
        product: ProductKnowledge,
        plan: BudgetPlan,
        intent: CommercialIntent,
    ) -> float:
        # La afinidad de industria es la señal dominante; semantic queda reducido.
        base = (
            trace.semantic_score * profile.weight_semantic
            + trace.context_score * profile.weight_context
            + trace.occasion_score * profile.weight_occasion
            + trace.commercial_score / 100 * profile.weight_commercial
            + trace.budget_score * profile.weight_budget_util
            + trace.availability_score * profile.weight_availability
            + trace.industry_score * 5.0
            + trace.affinity_score * profile.weight_industry
        )
        adjustment = 0.0
        text = self._product_signals(product)
        # Penalizacion comercial fuerte por categoria incompatible con industria.
        if intent.industry and self.industry_knowledge.is_avoided(
            intent.industry, text
        ):
            adjustment -= 60
        # Penalizacion general comercial (no excluye, pero baja la prioridad).
        if self.industry_knowledge.is_general_blacklisted(text):
            adjustment -= 30
        if profile.prefer_premium:
            if product.perceived_value_level == "alto":
                adjustment += 12
            elif any(m in text for m in PREMIUM_MATERIALS):
                adjustment += 8
        if profile.prefer_eco and self._is_eco(product):
            adjustment += 12
        if profile.prefer_low_cost and plan.per_unit_ceiling > 0:
            ratio = product.price.amount / plan.per_unit_ceiling
            adjustment += 6 * (1.0 - min(1.0, ratio))
        return base + adjustment

    def _reason(
        self, intent: CommercialIntent, product: ProductKnowledge, trace: DecisionTrace
    ) -> str:
        return generate_reason(product, intent, None, trace)

    def _is_eco(self, product: ProductKnowledge) -> bool:
        text = self._product_signals(product)
        return any(kw in text for kw in ECO_KEYWORDS)

    def _is_personalizable(self, product: ProductKnowledge) -> bool:
        text = self._product_signals(product)
        return any(kw in text for kw in PERSONALIZABLE_KEYWORDS)

    def complementarity_with(self, product: ProductKnowledge, others: List[ProductKnowledge]) -> float:
        if not others:
            return 1.0
        return sum(products_complement(product, o) for o in others) / len(others)

