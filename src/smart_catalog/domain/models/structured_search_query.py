from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StructuredSearchQuery:
    original_query: str
    normalized_query: str
    detected_categories: list[str] = field(default_factory=list)
    detected_materials: list[str] = field(default_factory=list)
    detected_price_intent: Optional[str] = None
    detected_quality_intent: Optional[str] = None
    detected_eco_intent: bool = False
    detected_product_types: list[str] = field(default_factory=list)
    detected_audience: Optional[str] = None
    detected_colors: list[str] = field(default_factory=list)
    detected_attributes: list[str] = field(default_factory=list)
    unknown_terms: list[str] = field(default_factory=list)
    confidence: float = 0.0
