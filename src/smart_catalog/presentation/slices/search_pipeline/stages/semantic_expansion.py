from ...search_pipeline.context import SearchContext
from ...semantic_query_expansion.service import SemanticQueryExpansionService


class SemanticExpansionStage:
    def __init__(self, service: SemanticQueryExpansionService) -> None:
        self._service = service

    def execute(self, ctx: SearchContext) -> None:
        if ctx.structured_query is None or self._service is None:
            ctx.search_text = (ctx.structured_query.normalized_query
                               if ctx.structured_query else "") or ctx.original_query
            return
        ctx.expanded_query = self._service.expand(ctx.structured_query, ctx.intent)
        ctx.search_text = ctx.expanded_query.expanded_query
