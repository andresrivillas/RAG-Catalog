from abc import ABC, abstractmethod
from typing import Optional

from ..models.catalog_search_query import CatalogSearchQuery


class HistoryRepository(ABC):
    @abstractmethod
    def save(self, query: CatalogSearchQuery) -> None:
        ...

    @abstractmethod
    def get_recent(self, limit: int = 10) -> list[CatalogSearchQuery]:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...
