from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RecommendationOutput:
    query: str = ""
    audience: Optional[str] = None
    category: Optional[str] = None
    price_intent: Optional[str] = None
    quality_intent: Optional[str] = None
    eco_intent: bool = False
    technologies: list[str] = field(default_factory=list)

    preferred_product_families: list[str] = field(default_factory=list)
    preferred_categories: list[str] = field(default_factory=list)
    preferred_materials: list[str] = field(default_factory=list)
    preferred_attributes: list[str] = field(default_factory=list)
    preferred_technologies: list[str] = field(default_factory=list)

    avoid_product_families: list[str] = field(default_factory=list)
    avoid_categories: list[str] = field(default_factory=list)
    avoid_materials: list[str] = field(default_factory=list)

    use_cases: list[str] = field(default_factory=list)
    reason: str = ""
