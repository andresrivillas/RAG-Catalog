import logging
from typing import Optional, Union

from ....domain.models.search_response import SearchResponse
from ....domain.models.structured_search_query import StructuredSearchQuery
from ....infrastructure.services.chroma_catalog_search_service import (
    ChromaCatalogSearchService,
)
from ..search_ranking.service import SearchRankingService
from ..semantic_query_expansion.service import SemanticQueryExpansionService
from ..search_explanation.service import SearchExplanationService
from ..intent_resolution.service import IntentResolutionService
from ....commercial_knowledge.service import CommercialKnowledgeService
from ..search_pipeline.pipeline import SearchPipeline
from ..search_pipeline.stages.intent_resolution import IntentResolutionStage
from ..search_pipeline.stages.semantic_expansion import SemanticExpansionStage
from ..search_pipeline.stages.vector_search import VectorSearchStage
from ..search_pipeline.stages.family_boost import FamilyBoostStage
from ..search_pipeline.stages.ranking import RankingStage
from ..search_pipeline.stages.explanation import ExplanationStage
from ..search_pipeline.stages.commercial_affinity import CommercialAffinityStage

logger = logging.getLogger("smart_catalog.search")


class SearchCatalogService:
    def __init__(
        self,
        search_service: ChromaCatalogSearchService,
        ranking_service: Optional[SearchRankingService] = None,
        expansion_service: Optional[SemanticQueryExpansionService] = None,
        explanation_service: Optional[SearchExplanationService] = None,
        intent_service: Optional[IntentResolutionService] = None,
        commercial_service: Optional[CommercialKnowledgeService] = None,
    ) -> None:
        self._pipeline = SearchPipeline(
            intent_stage=IntentResolutionStage(intent_service),
            expansion_stage=SemanticExpansionStage(expansion_service),
            vector_stage=VectorSearchStage(search_service),
            family_stage=FamilyBoostStage(),
            ranking_stage=RankingStage(ranking_service),
            explanation_stage=ExplanationStage(explanation_service),
            commercial_stage=CommercialAffinityStage(commercial_service),
        )

    def search(
        self,
        query: Union[str, StructuredSearchQuery],
        max_results: int = 20,
    ) -> SearchResponse:
        return self._pipeline.run(query, max_results=max_results)
