from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CommercialIntent:
    raw_text: str = ""
    occasion: Optional[str] = None
    quantity: Optional[int] = None
    budget_total: Optional[float] = None
    budget_per_unit: Optional[float] = None
    target_audience: Optional[str] = None
    preferred_categories: List[str] = field(default_factory=list)
    preferred_materials: List[str] = field(default_factory=list)
    preferred_colors: List[str] = field(default_factory=list)
    eco: bool = False
    personalizable: bool = False
    packaging_required: bool = False
    generation_mode: str = "balanced"
