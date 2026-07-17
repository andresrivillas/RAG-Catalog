from ...search_pipeline.context import SearchContext
from ...intent_resolution.service import IntentResolutionService


class IntentResolutionStage:
    def __init__(self, service: IntentResolutionService) -> None:
        self._service = service

    def execute(self, ctx: SearchContext) -> None:
        if ctx.structured_query is not None and self._service is not None:
            ctx.intent = self._service.resolve(ctx.structured_query)
