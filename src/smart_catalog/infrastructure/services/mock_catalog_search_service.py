from ...domain.models.catalog_search_query import CatalogSearchQuery
from ...domain.models.search_response import SearchResponse
from ...domain.models.search_metadata import SearchMetadata
from ...domain.ports.catalog_search_service import CatalogSearchService


class MockCatalogSearchService(CatalogSearchService):
    def search(self, query: CatalogSearchQuery) -> SearchResponse:
        return SearchResponse(
            query=query.text,
            results=[],
            total_results=0,
            metadata=SearchMetadata(
                processing_time_ms=0.0,
                total_candidates=0,
                results_returned=0,
                embedding_used=False,
                keyword_used=False,
            ),
        )
