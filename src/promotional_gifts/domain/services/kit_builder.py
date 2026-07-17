from dataclasses import dataclass, field
from typing import List, Optional

from ..entities.commercial_intent import CommercialIntent
from ..entities.product_knowledge import ProductKnowledge
from ..services.budget_plan import BudgetPlan
from ..services.compatibility_checker import CompatibilityChecker
from ..services.generation_mode import GenerationMode, get_profile
from ..services.perceived_value import PerceivedValueEstimator
from ..services.product_selector import ScoredProduct
from ..services.reason_generator import generate as generate_reason
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
    mode: GenerationMode = None
    concept: str = ""


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
        anchors = self._ordered_anchors(scored_products)
        kits: List[List[KitLine]] = []

        for i in range(self.config.num_kits):
            if i >= len(anchors):
                break
            anchor = anchors[i]
            kit = self._build_kit(anchor, scored_products, plan, scored_by_ref, intent)
            if kit:
                upgraded = self._upgrade_to_budget(kit, scored_products, plan, scored_by_ref, intent)
                kits.append(upgraded)
        return kits

    def _ordered_anchors(
        self, scored_products: List[ScoredProduct]
    ) -> List[ScoredProduct]:
        import copy

        profile = get_profile(self.config.mode)
        # Descartar productos con baja armonía o valor percibido bajo en premium.
        def anchor_eligible(sp: ScoredProduct) -> bool:
            if getattr(sp.trace, "harmony_score", 1.0) < 0.5:
                return False
            if profile.prefer_premium and sp.product.perceived_value_level == "bajo":
                return False
            return True

        ordered = [sp for sp in scored_products if anchor_eligible(sp)]
        if not ordered:
            ordered = list(scored_products)

        if profile.prefer_premium:
            ordered.sort(
                key=lambda sp: (
                    0 if sp.product.perceived_value_level == "alto" else 1,
                    -getattr(sp.trace, "commercial_value_score", 0.0),
                    -sp.product.price.amount,
                )
            )
        elif profile.prefer_low_cost:
            ordered.sort(
                key=lambda sp: (
                    -getattr(sp.trace, "harmony_score", 1.0),
                    sp.product.price.amount,
                ),
            )
        elif profile.prefer_eco:
            ordered.sort(
                key=lambda sp: (
                    0 if self._is_eco(sp.product) else 1,
                    getattr(sp.trace, "harmony_score", 1.0),
                    -sp.trace.final_score,
                )
            )
        else:
            ordered.sort(
                key=lambda sp: (
                    -getattr(sp.trace, "harmony_score", 1.0),
                    -sp.trace.final_score,
                ),
            )
        need = self.config.num_kits * 2
        if len(ordered) > need:
            ordered = ordered[:need]
        return ordered

    @staticmethod
    def _is_eco(product) -> bool:
        text = (
            f"{product.name} {product.description} {product.materials} "
            f"{' '.join(product.commercial_tags)}".lower()
        )
        return any(
            kw in text
            for kw in ["eco", "ecologico", "ecológico", "sostenible", "rpet", "recicl"]
        )

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

    ROLE_FILL_ORDER = ["CORE", "UTILITY", "PROMOTIONAL", "ACCESSORY", "PACKAGING"]

    ROLE_MAX = {
        "CORE": 1,
        "UTILITY": 2,
        "PREMIUM": 1,
        "PROMOTIONAL": 1,
        "ACCESSORY": 1,
        "PACKAGING": 1,
    }

    def _role_max(self, role: str) -> int:
        profile = get_profile(self.config.mode)
        if profile.prefer_low_cost:
            if role == "UTILITY":
                return 4
            if role == "ACCESSORY":
                return 3
            if role == "PROMOTIONAL":
                return 2
        if profile.prefer_premium:
            if role == "PREMIUM":
                return 1
            if role == "UTILITY":
                return 1
            if role == "ACCESSORY":
                return 1
        return self.ROLE_MAX.get(role, 1)

    MODE_FILL_ORDER = {
        "BALANCED": ["CORE", "UTILITY", "PROMOTIONAL", "ACCESSORY", "PACKAGING"],
        "PREMIUM": ["CORE", "PREMIUM", "UTILITY", "ACCESSORY", "PROMOTIONAL", "PACKAGING"],
        "BUDGET": ["UTILITY", "PROMOTIONAL", "ACCESSORY", "CORE", "PACKAGING"],
        "ECO": ["CORE", "UTILITY", "ACCESSORY", "PROMOTIONAL", "PACKAGING"],
    }

    def _role_fill_order(self) -> List[str]:
        mode = (self.config.mode or GenerationMode.BALANCED).value
        return self.MODE_FILL_ORDER.get(mode, self.MODE_FILL_ORDER["BALANCED"])

    def _build_kit(
        self,
        anchor: ScoredProduct,
        pool: List[ScoredProduct],
        plan: BudgetPlan,
        scored_by_ref: dict,
        intent: CommercialIntent,
    ) -> List[KitLine]:
        lines: List[KitLine] = []
        roles_used: dict = {}
        remaining = plan.spendable_budget

        if anchor.product.price.amount <= 0:
            return []

        # Si el ancla original absorbe casi todo el presupuesto, se busca un
        # ancla alternativo que deje espacio para completar el kit (CORE +
        # UTILITY + PROMOTIONAL + ACCESSORY + PACKAGING) sin reducir mucho el
        # puntaje. Solo se cambia cuando el ancla original impide un kit completo.
        anchor = self._fit_anchor(anchor, pool, plan)

        anchor_role = self.role_classifier.classify(
            anchor.product, self.config.price_median
        )
        lines.append(
            KitLine(
                anchor.product,
                anchor_role,
                generate_reason(anchor.product, intent, anchor_role, anchor.trace, concept=self.config.concept),
                anchor.trace,
            )
        )
        roles_used[anchor_role] = roles_used.get(anchor_role, 0) + 1
        remaining -= anchor.product.price.amount * plan.quantity

        # Rellenar el kit en el orden recomendado de roles para lograr
        # kits completos (CORE -> UTILITY -> PROMOTIONAL -> ACCESSORY -> PACKAGING).
        ordered_pool = self._order_by_role_and_score(pool, anchor)
        for candidate in ordered_pool:
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
            # Penalizar productos que rompen el concepto del kit.
            # En modo budget se relaja ligeramente para permitir mayor cobertura.
            min_harmony = 0.25 if get_profile(self.config.mode).prefer_low_cost else 0.35
            if getattr(candidate.trace, "harmony_score", 1.0) < min_harmony:
                continue

            role = self.role_classifier.classify(
                candidate.product, self.config.price_median
            )
            if role == "PREMIUM":
                role = "CORE"
            if role == "CORE" and roles_used.get("CORE", 0) >= self._role_max("CORE"):
                role = "UTILITY"
            if roles_used.get(role, 0) >= self._role_max(role):
                continue

            lines.append(
                KitLine(
                    candidate.product,
                    role,
                    generate_reason(candidate.product, intent, role, candidate.trace, concept=self.config.concept),
                    candidate.trace,
                )
            )
            roles_used[role] = roles_used.get(role, 0) + 1
            remaining -= candidate.product.price.amount * plan.quantity

            if len(lines) >= self.config.min_lines and remaining <= 0:
                break

        # Si aun faltan lineas para el minimo y queda presupuesto, anadir
        # productos utiles aunque no cubran un rol nuevo.
        if len(lines) < self.config.min_lines:
            for candidate in ordered_pool:
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
                if any(
                    not self.compatibility.can_coexist(l.product, candidate.product)
                    for l in lines
                ):
                    continue
                min_harmony_fallback = 0.15 if get_profile(self.config.mode).prefer_low_cost else 0.25
                if getattr(candidate.trace, "harmony_score", 1.0) < min_harmony_fallback:
                    continue
                role = self.role_classifier.classify(
                    candidate.product, self.config.price_median
                )
                if role == "PREMIUM":
                    role = "CORE"
                if role == "CORE" and roles_used.get("CORE", 0) >= self._role_max("CORE"):
                    role = "UTILITY"
                if roles_used.get(role, 0) >= self._role_max(role):
                    continue
                lines.append(
                    KitLine(
                        candidate.product,
                        role,
                        generate_reason(candidate.product, intent, role, candidate.trace, concept=self.config.concept),
                        candidate.trace,
                    )
                )
                roles_used[role] = roles_used.get(role, 0) + 1
                remaining -= candidate.product.price.amount * plan.quantity

        return lines

    def _order_by_role_and_score(
        self, pool: List[ScoredProduct], anchor: ScoredProduct
    ) -> List[ScoredProduct]:
        fill_order = self._role_fill_order()

        def role_rank(sp: ScoredProduct) -> int:
            role = self.role_classifier.classify(
                sp.product, self.config.price_median
            )
            try:
                return fill_order.index(role)
            except ValueError:
                return len(fill_order)

        # Modo Premium: prioriza valor percibido y armonía.
        # Modo Budget: prioriza los productos mas economicos para maximizar lineas.
        # Modo Eco: prioriza productos eco cuando el score es cercano.
        profile = get_profile(self.config.mode)

        def harmony_rank(sp: ScoredProduct) -> float:
            return getattr(sp.trace, "harmony_score", 1.0)

        if profile.prefer_premium:
            sort_key = lambda sp: (
                role_rank(sp),
                -harmony_rank(sp),
                0 if sp.product.perceived_value_level == "alto" else 1,
                -sp.product.price.amount,
                -sp.score,
            )
        elif profile.prefer_eco:
            sort_key = lambda sp: (
                role_rank(sp),
                0 if self._is_eco(sp.product) else 1,
                -harmony_rank(sp),
                -sp.score,
            )
        elif profile.prefer_low_cost:
            sort_key = lambda sp: (
                role_rank(sp),
                -harmony_rank(sp),
                sp.product.price.amount,
                -sp.score,
            )
        else:
            sort_key = lambda sp: (
                role_rank(sp),
                -harmony_rank(sp),
                sp.product.price.amount,
                -sp.score,
            )

        return sorted(pool, key=sort_key)

    def _cheapest_price(self, pool: List[ScoredProduct]) -> float:
        valid = [sp.product.price.amount for sp in pool if sp.product.price.amount > 0]
        return min(valid) if valid else 0.0

    def _fit_anchor(
        self,
        anchor: ScoredProduct,
        pool: List[ScoredProduct],
        plan: BudgetPlan,
    ) -> ScoredProduct:
        if plan.quantity <= 0:
            return anchor
        if plan.per_unit_ceiling <= 0:
            return anchor
        # El espacio real disponible es el presupuesto usable por unidad,
        # no el techo bruto (el optimizador reserva un margen).
        unit_remaining = plan.spendable_budget / plan.quantity if plan.quantity > 0 else plan.per_unit_ceiling
        cheapest = self._cheapest_price(pool)
        # Costo por unidad que deberia dejar libre el ancla para completar el kit.
        room_needed = (self.config.min_lines - 1) * cheapest
        anchor_unit = anchor.product.price.amount
        if anchor_unit + room_needed <= unit_remaining * 1.02:
            return anchor
        # El ancla original deja muy poco espacio: buscar un ancla que permita
        # un kit completo sin sacrificar demasiado puntaje (>= 70% del ancla).
        candidates = [
            sp for sp in pool
            if sp.product.price.amount > 0
            and sp.product.price.amount + room_needed <= unit_remaining * 1.02
            and sp.score >= anchor.score * 0.7
        ]
        if not candidates:
            return anchor
        candidates.sort(key=lambda sp: sp.score, reverse=True)
        return candidates[0]

    def _budget_allows(
        self, product: ProductKnowledge, remaining: float, plan: BudgetPlan
    ) -> bool:
        return product.price.amount * plan.quantity <= remaining

    def _kit_cost(self, kit: List[KitLine], plan: BudgetPlan) -> float:
        return sum(line.product.price.amount for line in kit) * plan.quantity

    def _utilization(self, kit: List[KitLine], plan: BudgetPlan) -> float:
        if plan.spendable_budget <= 0:
            return 0.0
        return self._kit_cost(kit, plan) / plan.spendable_budget

    def _upgrade_to_budget(
        self,
        kit: List[KitLine],
        pool: List[ScoredProduct],
        plan: BudgetPlan,
        scored_by_ref: dict,
        intent: CommercialIntent,
    ) -> List[KitLine]:
        profile = get_profile(self.config.mode)
        target_min = profile.utilization_target_min
        target_max = profile.utilization_target_max
        target = (target_min + target_max) / 2.0

        max_rounds = 12
        for _ in range(max_rounds):
            util = self._utilization(kit, plan)
            if util >= target_min:
                break

            upgradable_roles = ("UTILITY", "ACCESSORY", "PACKAGING", "PROMOTIONAL")
            candidates_for_upgrade = [
                line for line in kit if line.role in upgradable_roles
            ]
            if not candidates_for_upgrade:
                break

            remaining = plan.spendable_budget - self._kit_cost(kit, plan)
            best_swap = None
            for line in candidates_for_upgrade:
                for candidate in pool:
                    cand = candidate.product
                    if cand.reference == line.product.reference:
                        continue
                    if cand.reference in {l.product.reference for l in kit}:
                        continue
                    if cand.price.amount <= line.product.price.amount:
                        continue
                    if not self._budget_allows(cand, remaining, plan):
                        continue
                    if not self.compatibility.can_coexist(line.product, cand):
                        continue
                    if any(
                        not self.compatibility.can_coexist(l.product, cand)
                        for l in kit if l is not line
                    ):
                        continue
                    min_harmony_upgrade = 0.25 if get_profile(self.config.mode).prefer_low_cost else 0.35
                    if getattr(candidate.trace, "harmony_score", 1.0) < min_harmony_upgrade:
                        continue
                    new_util = util + (cand.price.amount - line.product.price.amount) / plan.spendable_budget
                    if new_util > target_max:
                        continue
                    extra = cand.price.amount - line.product.price.amount
                    if best_swap is None or extra > best_swap[0]:
                        new_role = self.role_classifier.classify(
                            cand, self.config.price_median
                        )
                        if new_role == "PREMIUM":
                            new_role = "CORE"
                        best_swap = (
                            extra,
                            line,
                            KitLine(
                                cand,
                                new_role,
                                generate_reason(cand, intent, new_role, candidate.trace, concept=self.config.concept),
                                candidate.trace,
                            ),
                        )
            if best_swap is None:
                break
            extra, old_line, new_line = best_swap
            kit = [new_line if l is old_line else l for l in kit]

        return kit

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
        attrs = []
        if product.materials:
            attrs.append(f"material {product.materials}")
        if product.colors:
            attrs.append(f"color {product.colors}")
        if product.capacity:
            attrs.append(f"capacidad {product.capacity}")
        if product.customization:
            attrs.append("personalizable")
        if attrs:
            base += " Atributos: " + ", ".join(attrs) + "."
        if product.perceived_value_level == "alto":
            base += " Alto valor percibido."
        if getattr(plan, "eco_requested", False):
            base += " Cumple la restriccion ecologica."
        return base
