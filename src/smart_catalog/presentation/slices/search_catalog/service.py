import logging

from typing import Optional, Union

from ....domain.models.catalog_search_query import CatalogSearchQuery
from ....domain.models.search_response import SearchResponse
from ....domain.models.structured_search_query import StructuredSearchQuery
from ....infrastructure.services.chroma_catalog_search_service import (
    ChromaCatalogSearchService,
)
from ....shared.product_family_dictionary import is_product_in_family, get_family_key
from ..search_ranking.service import SearchRankingService
from ..semantic_query_expansion.service import SemanticQueryExpansionService
from ..search_explanation.service import SearchExplanationService
from ..intent_resolution.service import IntentResolutionService
from ....commercial_knowledge.service import CommercialKnowledgeService

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
        self._search_service = search_service
        self._ranking_service = ranking_service
        self._expansion_service = expansion_service
        self._explanation_service = explanation_service
        self._intent_service = intent_service
        self._commercial_service = commercial_service

    def search(
        self,
        query: Union[str, StructuredSearchQuery],
        max_results: int = 20,
    ) -> SearchResponse:
        expanded = None
        intent = None

        if isinstance(query, str):
            search_text = query
            original = query
            structured = None
        else:
            original = query.original_query
            structured = query

            if self._intent_service is not None:
                intent = self._intent_service.resolve(query)

            if self._expansion_service is not None:
                expanded = self._expansion_service.expand(query, intent)
                search_text = expanded.expanded_query
            else:
                search_text = query.normalized_query or query.original_query

        retrieval_k = max(max_results, 30)
        catalog_query = CatalogSearchQuery(text=search_text, max_results=retrieval_k)
        response = self._search_service.search(catalog_query)
        response.query = original

        if (
            intent
            and intent.intent_type == "PRODUCT_FAMILY"
            and intent.detected_product_family
        ):
            family_key = get_family_key(structured.detected_product_types)
            if family_key:
                family_matches = []
                others = []
                for r in response.results:
                    if is_product_in_family(
                        r.product.name,
                        r.product.category,
                        family_key,
                    ):
                        family_matches.append(r)
                    else:
                        others.append(r)
                response.results = family_matches + others
                response.total_results = len(response.results)
                for idx, r in enumerate(response.results):
                    r.rank = idx + 1

        if structured is not None and self._ranking_service is not None:
            ranked = self._ranking_service.rank(structured, response.results, intent)
            response.results = ranked[:max_results]
            response.total_results = len(response.results)

        if (
            structured is not None
            and self._explanation_service is not None
        ):
            response = self._explanation_service.explain(
                structured, expanded, response, intent,
            )

        if (
            structured is not None
            and self._commercial_service is not None
        ):
            response = self._commercial_service.enhance(
                response, structured, intent,
            )

        return response
