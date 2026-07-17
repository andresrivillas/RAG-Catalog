from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SearchIntent:
    intent_type: str = "UNKNOWN"
    confidence: float = 0.0
    detected_product_family: Optional[str] = None
    detected_category: Optional[str] = None
    detected_concept: Optional[str] = None
    detected_constraints: list[str] = field(default_factory=list)
    detected_audience: Optional[str] = None
    detected_materials: list[str] = field(default_factory=list)
    detected_price_intent: Optional[str] = None
    detected_quality_intent: Optional[str] = None
    reason: str = ""
