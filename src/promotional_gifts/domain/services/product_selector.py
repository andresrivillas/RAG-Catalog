from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from ..entities.commercial_intent import CommercialIntent
from ..entities.product_knowledge import ProductKnowledge
from ..services.budget_plan import BudgetPlan
from ..services.commercial_scorer import CommercialScorer
from ..services.decision_trace import DecisionTrace
from ..services.generation_mode import GenerationMode, ModeProfile, get_profile
from ..services.negative_filter import NegativeFilter
from ..services.occasion_matcher import OccasionMatcher

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
    ) -> None:
        self.occasion_matcher = occasion_matcher
        self.commercial_scorer = commercial_scorer
        self.negative_filter = negative_filter

    def select(
        self,
        candidates: List[Tuple[ProductKnowledge, float]],
        intent: CommercialIntent,
        plan: BudgetPlan,
        mode: GenerationMode = None,
    ) -> List[ScoredProduct]:
        profile = get_profile(mode)
        eligible: List[ScoredProduct] = []

        for product, similarity in candidates:
            trace = DecisionTrace(semantic_score=max(0.0, min(1.0, similarity)))

            if not self._valid_price(product):
                trace.reason = "Precio inválido o ausente; excluido."
                continue
            if self.negative_filter.is_excluded(product):
                trace.reason = "Categoría incompatible (filtro negativo)."
                continue
            if not self._passes_intent_filters(product, intent, plan, trace):
                continue

            trace.occasion_score = self.occasion_matcher.score(intent, product)
            trace.commercial_score = self.commercial_scorer.score(intent, product)
            trace.budget_score = self._budget_utilization_score(product, plan, profile)
            trace.final_score = self._combine(trace, profile, product, plan)
            trace.reason = self._reason(intent, product, trace)
            eligible.append(ScoredProduct(product, similarity, trace.final_score, trace))

        eligible.sort(key=lambda sp: sp.score, reverse=True)
        return eligible

    def _valid_price(self, product: ProductKnowledge) -> bool:
        return product.price.amount > 0

    def _passes_intent_filters(
        self,
        product: ProductKnowledge,
        intent: CommercialIntent,
        plan: BudgetPlan,
        trace: DecisionTrace,
    ) -> bool:
        if product.price.amount > plan.per_unit_ceiling:
            trace.reason = "Supera el presupuesto por unidad."
            return False
        if intent.eco and not self._is_eco(product):
            trace.reason = "No cumple restricción ecológica."
            return False
        if intent.personalizable and not self._is_personalizable(product):
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

    def _combine(
        self,
        trace: DecisionTrace,
        profile: ModeProfile,
        product: ProductKnowledge,
        plan: BudgetPlan,
    ) -> float:
        base = (
            trace.semantic_score * profile.weight_semantic
            + trace.occasion_score * profile.weight_occasion
            + trace.commercial_score / 100 * profile.weight_commercial
            + trace.budget_score * profile.weight_budget_util
        )
        adjustment = 0.0
        text = (
            f"{product.name} {product.description} {product.materials} "
            f"{' '.join(product.commercial_tags)}".lower()
        )
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
        parts = []
        if intent.occasion:
            parts.append(
                f"adecuado para {intent.occasion}"
                if trace.occasion_score >= 0.7
                else f"relacionado con {intent.occasion}"
            )
        if product.perceived_value_level == "alto":
            parts.append("alto valor percibido")
        if "personalizable" in product.commercial_tags:
            parts.append("personalizable")
        parts.append("cumple el presupuesto")
        return "Seleccionado por " + "; ".join(parts) + "."

    def _is_eco(self, product: ProductKnowledge) -> bool:
        text = (
            f"{product.name} {product.description} {product.materials} "
            f"{' '.join(product.commercial_tags)}".lower()
        )
        return any(kw in text for kw in ECO_KEYWORDS)

    def _is_personalizable(self, product: ProductKnowledge) -> bool:
        text = (
            f"{product.name} {product.description} {product.materials} "
            f"{' '.join(product.commercial_tags)}".lower()
        )
        return any(kw in text for kw in PERSONALIZABLE_KEYWORDS)
