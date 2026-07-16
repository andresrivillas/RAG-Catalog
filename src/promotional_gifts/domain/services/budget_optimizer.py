from ..entities.commercial_intent import CommercialIntent
from ..services.budget_plan import BudgetPlan


class BudgetOptimizer:
    MARGIN_RESERVE_PCT = 0.05

    def optimize(self, intent: CommercialIntent) -> BudgetPlan:
        quantity = intent.quantity or 1
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

        spendable_budget = total_budget - margin_reserve
        return BudgetPlan(
            total_budget=total_budget,
            spendable_budget=spendable_budget,
            per_unit_ceiling=per_unit_ceiling,
            margin_reserve=margin_reserve,
            quantity=quantity,
            eco_requested=intent.eco,
        )
