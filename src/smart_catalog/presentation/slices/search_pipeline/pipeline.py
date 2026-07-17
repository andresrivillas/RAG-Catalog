import logging
from typing import Union

from ....domain.models.search_response import SearchResponse
from ....domain.models.structured_search_query import StructuredSearchQuery
from .context import SearchContext
from .stages.intent_resolution import IntentResolutionStage
from .stages.semantic_expansion import SemanticExpansionStage
from .stages.vector_search import VectorSearchStage
from .stages.family_boost import FamilyBoostStage
from .stages.ranking import RankingStage
from .stages.explanation import ExplanationStage
from .stages.commercial_affinity import CommercialAffinityStage

logger = logging.getLogger("smart_catalog.search")


class SearchPipeline:
    def __init__(
        self,
        intent_stage: IntentResolutionStage,
        expansion_stage: SemanticExpansionStage,
        vector_stage: VectorSearchStage,
        family_stage: FamilyBoostStage,
        ranking_stage: RankingStage,
        explanation_stage: ExplanationStage,
        commercial_stage: CommercialAffinityStage,
    ) -> None:
        self._stages = [
            intent_stage,
            expansion_stage,
            vector_stage,
            family_stage,
            ranking_stage,
            explanation_stage,
            commercial_stage,
        ]

    def run(
        self,
        query: Union[str, StructuredSearchQuery],
        max_results: int = 20,
    ) -> SearchResponse:
        ctx = SearchContext()

        if isinstance(query, str):
            ctx.original_query = query
            ctx.search_text = query
        else:
            ctx.original_query = query.original_query
            ctx.structured_query = query

        ctx.max_results = max_results

        for stage in self._stages:
            stage.execute(ctx)

        return ctx.response
