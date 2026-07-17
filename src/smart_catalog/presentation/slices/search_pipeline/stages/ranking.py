from ...search_pipeline.context import SearchContext
from ...search_ranking.service import SearchRankingService


class RankingStage:
    def __init__(self, service: SearchRankingService) -> None:
        self._service = service

    def execute(self, ctx: SearchContext) -> None:
        if ctx.structured_query is None or self._service is None or ctx.response is None:
            return
        ranked = self._service.rank(ctx.structured_query, ctx.response.results, ctx.intent)
        ctx.response.results = ranked[:ctx.max_results]
        ctx.response.total_results = len(ctx.response.results)
