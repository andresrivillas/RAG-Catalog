from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CatalogProduct:
    reference: str
    name: str
    description: str = ""
    category: str = ""
    subcategory: str = ""
    price: float = 0.0
    currency: str = "COP"
    material: str = ""
    colors: str = ""
    dimensions: str = ""
    weight: str = ""
    eco_friendly: bool = False
    personalizable: bool = False
    image_url: Optional[str] = None
    detail_url: Optional[str] = None
    is_net_price: bool = False
    perceived_value_level: str = ""
    tags: list[str] = field(default_factory=list)
    score: float = 0.0
