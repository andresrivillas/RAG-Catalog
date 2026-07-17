from .....domain.models.catalog_search_query import CatalogSearchQuery
from .....infrastructure.services.chroma_catalog_search_service import ChromaCatalogSearchService
from ...search_pipeline.context import SearchContext


class VectorSearchStage:
    def __init__(self, service: ChromaCatalogSearchService) -> None:
        self._service = service

    def execute(self, ctx: SearchContext) -> None:
        retrieval_k = max(ctx.max_results, 30)
        catalog_query = CatalogSearchQuery(text=ctx.search_text, max_results=retrieval_k)
        ctx.response = self._service.search(catalog_query)
        ctx.response.query = ctx.original_query
