from ...search_pipeline.context import SearchContext
from .....commercial_knowledge.service import CommercialKnowledgeService


class CommercialAffinityStage:
    def __init__(self, service: CommercialKnowledgeService) -> None:
        self._service = service

    def execute(self, ctx: SearchContext) -> None:
        if (
            ctx.structured_query is None
            or self._service is None
            or ctx.response is None
        ):
            return
        ctx.response = self._service.enhance(ctx.response, ctx.structured_query, ctx.intent)
