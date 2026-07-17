from abc import ABC, abstractmethod

from ..models.catalog_search_query import CatalogSearchQuery
from ..models.search_response import SearchResponse


class CatalogSearchService(ABC):
    @abstractmethod
    def search(self, query: CatalogSearchQuery) -> SearchResponse:
        ...
