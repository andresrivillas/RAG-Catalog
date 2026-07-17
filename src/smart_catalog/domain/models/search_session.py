from dataclasses import dataclass, field
from typing import Optional

from .structured_search_query import StructuredSearchQuery
from .expanded_search_query import ExpandedSearchQuery
from .search_response import SearchResponse


@dataclass
class SearchSession:
    session_id: str = ""
    current_query: str = ""
    previous_queries: list[str] = field(default_factory=list)
    current_structured: Optional[StructuredSearchQuery] = None
    current_expanded: Optional[ExpandedSearchQuery] = None
    current_results: Optional[SearchResponse] = None
    history: list[dict] = field(default_factory=list)
