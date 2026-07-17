from dataclasses import dataclass, field
from typing import List


@dataclass
class DecisionTrace:
    semantic_score: float = 0.0
    commercial_score: float = 0.0
    occasion_score: float = 0.0
    budget_score: float = 0.0
    context_score: float = 0.0
    industry_score: float = 0.0
    affinity_score: float = 0.0
    availability_score: float = 0.0
    commercial_value_score: float = 0.0
    harmony_score: float = 0.0
    final_score: float = 0.0
    reason: str = ""
    detail: dict = field(default_factory=dict)
