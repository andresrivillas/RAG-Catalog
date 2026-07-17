import logging
import time
from typing import Optional

from ....domain.models.expanded_search_query import ExpandedSearchQuery
from ....domain.models.search_intent import SearchIntent
from ....domain.models.search_response import SearchResponse
from ....domain.models.structured_search_query import StructuredSearchQuery
from .engine import SearchExplanationEngine

logger = logging.getLogger("smart_catalog.explanation")


class SearchExplanationService:
    def __init__(
        self,
        engine: Optional[SearchExplanationEngine] = None,
    ) -> None:
        self._engine = engine or SearchExplanationEngine()

    def explain(
        self,
        structured: StructuredSearchQuery,
        expanded: Optional[ExpandedSearchQuery],
        response: SearchResponse,
        intent: Optional[SearchIntent] = None,
    ) -> SearchResponse:
        start = time.perf_counter()

        for result in response.results:
            explanation = self._engine.explain(
                structured=structured,
                expanded=expanded,
                product=result.product,
                relevance_score=result.relevance_score,
                intent=intent,
            )
            result.explanation = explanation

        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            "Explicaciones generadas para %d resultados en %.1fms",
            len(response.results), elapsed,
        )

        return response
