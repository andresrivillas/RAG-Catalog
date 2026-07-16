from ..entities.commercial_intent import CommercialIntent
from .generation_mode import GenerationMode, get_profile
from .budget_plan import BudgetPlan


class BudgetOptimizer:
    MARGIN_RESERVE_PCT = 0.05
    # Valores por defecto para solicitudes genericas (sin cantidad ni
    # presupuesto) de modo que el sistema siempre devuelva propuestas.
    DEFAULT_QUANTITY = 100
    DEFAULT_PER_UNIT_CEILING = 15000.0

    def optimize(
        self, intent: CommercialIntent, mode: GenerationMode = None
    ) -> BudgetPlan:
        quantity = intent.quantity or self.DEFAULT_QUANTITY
        margin_reserve = 0.0
        total_budget = 0.0
        per_unit_ceiling = 0.0

        if intent.budget_total is not None:
            total_budget = intent.budget_total
            margin_reserve = total_budget * self.MARGIN_RESERVE_PCT
            per_unit_ceiling = (total_budget - margin_reserve) / quantity
        elif intent.budget_per_unit is not None:
            per_unit_ceiling = intent.budget_per_unit
            total_budget = per_unit_ceiling * quantity
            margin_reserve = total_budget * self.MARGIN_RESERVE_PCT
        else:
            # Sin presupuesto declarado: se asume un techo por unidad razonable
            # para poder construir un kit (fallback inteligente).
            per_unit_ceiling = self.DEFAULT_PER_UNIT_CEILING
            total_budget = per_unit_ceiling * quantity
            margin_reserve = total_budget * self.MARGIN_RESERVE_PCT

        spendable_budget = total_budget - margin_reserve

        profile = get_profile(mode) if mode else None
        target = (
            (profile.utilization_target_min, profile.utilization_target_max)
            if profile
            else (0.80, 0.90)
        )

        return BudgetPlan(
            total_budget=total_budget,
            spendable_budget=spendable_budget,
            per_unit_ceiling=per_unit_ceiling,
            margin_reserve=margin_reserve,
            quantity=quantity,
            eco_requested=intent.eco,
            utilization_target=target,
        )
