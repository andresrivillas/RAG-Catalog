from abc import ABC, abstractmethod

from ..models.catalog_product import CatalogProduct
from ..models.search_ranking import SearchRanking


class SearchRankingService(ABC):
    @abstractmethod
    def rank(self, products: list[CatalogProduct], query: str) -> list[SearchRanking]:
        ...
