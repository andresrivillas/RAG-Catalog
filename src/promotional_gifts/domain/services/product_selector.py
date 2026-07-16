from dataclasses import dataclass
from typing import List, Tuple

from ..entities.commercial_intent import CommercialIntent
from ..entities.product_knowledge import ProductKnowledge
from ..services.budget_plan import BudgetPlan

OCCASION_KEYWORDS = {
    "cumpleanos": ["cumple", "fiesta", "celebra", "party"],
    "navidad": ["navidad", "navideño", "navideña", "christmas"],
    "bienvenida": ["bienvenida", "welcome", "onboarding"],
    "evento": ["evento", "feria", "congreso"],
    "campana": ["campaña", "campana", "promo", "marketing"],
}

ECO_KEYWORDS = ["eco", "ecologico", "ecológico", "sostenible", "rpet", "recicl"]


@dataclass
class ScoredProduct:
    product: ProductKnowledge
    similarity: float
    score: float


class ProductSelector:
    def select(
        self,
        candidates: List[Tuple[ProductKnowledge, float]],
        intent: CommercialIntent,
        budget: BudgetPlan,
    ) -> List[ScoredProduct]:
        eligible: List[ScoredProduct] = []

        for product, similarity in candidates:
            if not self._passes_hard_filters(product, intent, budget):
                continue
            score = self._score(product, similarity, intent, budget)
            eligible.append(ScoredProduct(product, similarity, score))

        eligible.sort(key=lambda sp: sp.score, reverse=True)
        return eligible

    def _passes_hard_filters(
        self,
        product: ProductKnowledge,
        intent: CommercialIntent,
        budget: BudgetPlan,
    ) -> bool:
        if product.price.amount > budget.per_unit_ceiling:
            return False
        if intent.eco and not self._is_eco(product):
            return False
        if intent.personalizable and not self._is_personalizable(product):
            return False
        if intent.preferred_materials and not self._matches_any(
            product, intent.preferred_materials
        ):
            return False
        if intent.preferred_colors and not self._matches_any(
            product, intent.preferred_colors
        ):
            return False
        return True

    def _score(
        self,
        product: ProductKnowledge,
        similarity: float,
        intent: CommercialIntent,
        budget: BudgetPlan,
    ) -> float:
        sim_score = max(0.0, min(1.0, similarity)) * 50
        price_ratio = (
            product.price.amount / budget.per_unit_ceiling
            if budget.per_unit_ceiling > 0
            else 0.0
        )
        price_score = (1.0 - min(price_ratio, 1.0)) * 30
        value_score = self._perceived_value_score(product) * 20
        return sim_score + price_score + value_score

    def _perceived_value_score(self, product: ProductKnowledge) -> float:
        return {"alto": 1.0, "medio": 0.6, "bajo": 0.3}.get(
            product.perceived_value_level, 0.6
        )

    def _is_eco(self, product: ProductKnowledge) -> bool:
        text = f"{product.name} {product.description} {product.characteristics}".lower()
        return any(kw in text for kw in ECO_KEYWORDS)

    def _is_personalizable(self, product: ProductKnowledge) -> bool:
        text = f"{product.name} {product.description} {product.characteristics}".lower()
        return any(
            kw in text
            for kw in ["logo", "grabado", "personaliz", "marca", "tampografia", "tampografía"]
        )

    def _matches_any(self, product: ProductKnowledge, keywords: List[str]) -> bool:
        text = f"{product.name} {product.description} {product.characteristics}".lower()
        return any(kw.lower() in text for kw in keywords)

    def _occasion_affinity(
        self, product: ProductKnowledge, occasion: str
    ) -> float:
        keywords = OCCASION_KEYWORDS.get(occasion, [])
        text = f"{product.name} {product.description}".lower()
        return 1.0 if any(kw in text for kw in keywords) else 0.0
