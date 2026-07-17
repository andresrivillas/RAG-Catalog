from ...domain.models.catalog_product import CatalogProduct
from ...domain.models.search_ranking import SearchRanking
from ...domain.ports.search_ranking_service import SearchRankingService


class MockSearchRankingService(SearchRankingService):
    def rank(self, products: list[CatalogProduct], query: str) -> list[SearchRanking]:
        return []
