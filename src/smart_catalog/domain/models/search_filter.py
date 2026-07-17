from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SearchFilter:
    category: Optional[str] = None
    subcategory: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    eco_friendly: Optional[bool] = None
    personalizable: Optional[bool] = None
    material: Optional[str] = None
    tags: list[str] = field(default_factory=list)
