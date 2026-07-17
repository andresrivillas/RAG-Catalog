from dataclasses import dataclass, field
from typing import Optional

from .structured_search_query import StructuredSearchQuery


@dataclass
class ExpandedSearchQuery:
    original_query: str
    normalized_query: str
    expanded_terms: list[str] = field(default_factory=list)
    expanded_query: str = ""
    expansion_reason: str = ""
    confidence: float = 0.0
    structured_query: Optional[StructuredSearchQuery] = None
