from dataclasses import dataclass


@dataclass
class BudgetPlan:
    total_budget: float
    spendable_budget: float
    per_unit_ceiling: float
    margin_reserve: float
    quantity: int
