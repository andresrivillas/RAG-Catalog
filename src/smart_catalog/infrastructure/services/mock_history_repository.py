from typing import Optional

from ...domain.models.catalog_search_query import CatalogSearchQuery
from ...domain.ports.history_repository import HistoryRepository


class MockHistoryRepository(HistoryRepository):
    def save(self, query: CatalogSearchQuery) -> None:
        pass

    def get_recent(self, limit: int = 10) -> list[CatalogSearchQuery]:
        return []

    def clear(self) -> None:
        pass
