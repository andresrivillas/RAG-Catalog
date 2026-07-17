from dataclasses import dataclass, field
from typing import Optional

from .catalog_search_result import CatalogSearchResult
from .search_metadata import SearchMetadata


@dataclass
class SearchResponse:
    query: str
    results: list[CatalogSearchResult] = field(default_factory=list)
    total_results: int = 0
    metadata: Optional[SearchMetadata] = None
