from dataclasses import dataclass, field
from typing import List, Optional

from ..entities.commercial_intent import CommercialIntent
from ..entities.product_knowledge import ProductKnowledge
from ..services.budget_plan import BudgetPlan
from ..services.compatibility_checker import CompatibilityChecker
from ..services.perceived_value import PerceivedValueEstimator
from ..services.product_selector import ScoredProduct
from ..services.role_classifier import RoleClassifier


@dataclass
class KitLine:
    product: ProductKnowledge
    role: str
    reason: str = ""
    trace: object = None


@dataclass
class KitBuildConfig:
    num_kits: int = 3
    min_lines: int = 2
    max_lines: int = 5
    price_median: float = 0.0


class KitBuilder:
    def __init__(self, config: KitBuildConfig = None) -> None:
        self.config = config or KitBuildConfig()
        self.role_classifier = RoleClassifier()
        self.compatibility = CompatibilityChecker()
        self.value_estimator = PerceivedValueEstimator()

    def build(
        self,
        intent: CommercialIntent,
        scored_products: List[ScoredProduct],
        plan: BudgetPlan,
    ) -> List[List[KitLine]]:
        if not scored_products:
            return []

        classified = self._classify_all([sp.product for sp in scored_products])
        scored_by_ref = {sp.product.reference: sp for sp in scored_products}
        anchors = scored_products[: self.config.num_kits * 2] or scored_products
        kits: List[List[KitLine]] = []

        for i in range(self.config.num_kits):
            if i >= len(anchors):
                break
            anchor = anchors[i]
            kit = self._build_kit(anchor, scored_products, plan, scored_by_ref)
            if kit:
                kits.append(kit)
        return kits

    def _classify_all(
        self, products: List[ProductKnowledge]
    ) -> List[ProductKnowledge]:
        for p in products:
            if not p.perceived_value_level or p.perceived_value_level == "medio":
                if self.config.price_median > 0:
                    p.perceived_value_level = self.value_estimator.estimate(
                        p, self.config.price_median
                    )
        return products

    def _build_kit(
        self,
        anchor: ScoredProduct,
        pool: List[ScoredProduct],
        plan: BudgetPlan,
        scored_by_ref: dict,
    ) -> List[KitLine]:
        lines: List[KitLine] = []
        roles_used: dict = {}
        remaining = plan.spendable_budget

        if anchor.product.price.amount <= 0:
            return []

        anchor_role = self.role_classifier.classify(
            anchor.product, self.config.price_median
        )
        lines.append(
            KitLine(
                anchor.product,
                anchor_role,
                anchor.trace.reason if anchor.trace else "Producto principal del kit.",
                anchor.trace,
            )
        )
        roles_used[anchor_role] = roles_used.get(anchor_role, 0) + 1
        remaining -= anchor.product.price.amount * plan.quantity

        for candidate in pool:
            if len(lines) >= self.config.max_lines:
                break
            if candidate.product.reference == anchor.product.reference:
                continue
            if any(
                l.product.reference == candidate.product.reference for l in lines
            ):
                continue
            if candidate.product.price.amount <= 0:
                continue
            if not self._budget_allows(candidate.product, remaining, plan):
                continue
            if not self.compatibility.can_coexist(anchor.product, candidate.product):
                continue
            if any(
                not self.compatibility.can_coexist(l.product, candidate.product)
                for l in lines
            ):
                continue

            role = self.role_classifier.classify(
                candidate.product, self.config.price_median
            )
            if role == "CORE" and roles_used.get("CORE", 0) >= 1:
                role = "UTILITY"
            if role == "UTILITY" and roles_used.get("UTILITY", 0) >= 2:
                continue
            if role == "ACCESSORY" and roles_used.get("ACCESSORY", 0) >= 1:
                continue
            if (
                role in ("PACKAGING", "PROMOTIONAL")
                and roles_used.get(role, 0) >= 1
            ):
                continue

            reason = candidate.trace.reason if candidate.trace else self._reason(role, candidate.product, plan)
            lines.append(
                KitLine(candidate.product, role, reason, candidate.trace)
            )
            roles_used[role] = roles_used.get(role, 0) + 1
            remaining -= candidate.product.price.amount * plan.quantity

            if len(lines) >= self.config.min_lines and remaining <= 0:
                break

        return lines

    def _budget_allows(
        self, product: ProductKnowledge, remaining: float, plan: BudgetPlan
    ) -> bool:
        return product.price.amount * plan.quantity <= remaining

    def _reason(
        self,
        role: str,
        product: ProductKnowledge,
        plan: BudgetPlan,
    ) -> str:
        reasons = {
            "CORE": "Producto principal del kit.",
            "UTILITY": "Aporta utilidad diaria al destinatario.",
            "PREMIUM": "Mejora el valor percibido de la propuesta.",
            "ACCESSORY": f"Complementa el kit aportando coherencia.",
            "PACKAGING": "Empaque que presenta el regalo.",
            "PROMOTIONAL": "Refuerza la marca del cliente.",
        }
        base = reasons.get(role, "Producto seleccionado para la propuesta.")
        if product.perceived_value_level == "alto":
            base += " Alto valor percibido."
        if getattr(plan, "eco_requested", False):
            base += " Cumple la restricción ecológica."
        return base
