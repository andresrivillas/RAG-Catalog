from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SearchExplanation:
    reason: str = ""
    matched_terms: list[str] = field(default_factory=list)
    source: str = "keyword"

    primary_reason: str = ""
    secondary_reasons: list[str] = field(default_factory=list)
    matched_attributes: list[str] = field(default_factory=list)
    matched_materials: list[str] = field(default_factory=list)
    matched_categories: list[str] = field(default_factory=list)
    matched_price_intent: Optional[str] = None
    matched_quality_intent: Optional[str] = None
    matched_eco_intent: bool = False
    matched_audience: Optional[str] = None
    matched_colors: list[str] = field(default_factory=list)
    confidence: float = 0.0
    summary: str = ""
