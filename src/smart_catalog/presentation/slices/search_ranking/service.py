from typing import Optional
import logging
import time

from ....domain.models.catalog_search_result import CatalogSearchResult
from ....domain.models.search_intent import SearchIntent
from ....domain.models.structured_search_query import StructuredSearchQuery
from .engine import SearchRankingEngine, RankingWeights

logger = logging.getLogger("smart_catalog.ranking")


class SearchRankingService:
    def __init__(
        self,
        engine: Optional[SearchRankingEngine] = None,
    ) -> None:
        self._engine = engine or SearchRankingEngine()

    def rank(
        self,
        query: StructuredSearchQuery,
        results: list[CatalogSearchResult],
        intent: Optional[SearchIntent] = None,
    ) -> list[CatalogSearchResult]:
        start = time.perf_counter()

        ranked = self._engine.rank(query, results, intent)

        elapsed = (time.perf_counter() - start) * 1000

        if ranked:
            top = ranked[0]
            logger.info(
                "Ranking: %d productos reordenados en %.1fms | "
                "top: '%s' score=%.4f motivo='%s'",
                len(ranked), elapsed,
                top.product.name, top.relevance_score,
                top.explanation.reason if top.explanation else "",
            )
        else:
            logger.info("Ranking: 0 productos en %.1fms", elapsed)

        return ranked
