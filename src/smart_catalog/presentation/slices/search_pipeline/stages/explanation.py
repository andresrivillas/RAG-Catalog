from ...search_pipeline.context import SearchContext
from ...search_explanation.service import SearchExplanationService


class ExplanationStage:
    def __init__(self, service: SearchExplanationService) -> None:
        self._service = service

    def execute(self, ctx: SearchContext) -> None:
        if (
            ctx.structured_query is None
            or self._service is None
            or ctx.response is None
        ):
            return
        ctx.response = self._service.explain(
            ctx.structured_query, ctx.expanded_query, ctx.response, ctx.intent,
        )
