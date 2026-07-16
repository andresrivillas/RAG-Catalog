from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class BudgetPlan:
    total_budget: float
    spendable_budget: float
    per_unit_ceiling: float
    margin_reserve: float
    quantity: int
    eco_requested: bool = False
    utilization_target: Tuple[float, float] = field(default=(0.80, 0.90))
