from dataclasses import dataclass, field
from typing import Optional, Union

from ....domain.models.catalog_search_result import CatalogSearchResult
from ....domain.models.expanded_search_query import ExpandedSearchQuery
from ....domain.models.search_explanation import SearchExplanation
from ....domain.models.search_intent import SearchIntent
from ....domain.models.search_response import SearchResponse
from ....domain.models.structured_search_query import StructuredSearchQuery


@dataclass
class SearchContext:
    original_query: str = ""
    structured_query: Optional[StructuredSearchQuery] = None
    intent: Optional[SearchIntent] = None
    expanded_query: Optional[ExpandedSearchQuery] = None
    search_text: str = ""
    max_results: int = 20
    response: Optional[SearchResponse] = None
