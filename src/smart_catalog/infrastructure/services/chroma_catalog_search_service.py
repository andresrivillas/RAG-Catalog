import logging
import time

from ...domain.models.catalog_product import CatalogProduct
from ...domain.models.catalog_search_query import CatalogSearchQuery
from ...domain.models.catalog_search_result import CatalogSearchResult
from ...domain.models.search_explanation import SearchExplanation
from ...domain.models.search_metadata import SearchMetadata
from ...domain.models.search_response import SearchResponse
from ...domain.ports.catalog_search_service import CatalogSearchService
from ..vector_store.chroma_catalog_store import ChromaCatalogStore

logger = logging.getLogger("smart_catalog.search")


class ChromaCatalogSearchService(CatalogSearchService):
    def __init__(self, store: ChromaCatalogStore, top_k: int = 20) -> None:
        self._store = store
        self._top_k = top_k

    def search(self, query: CatalogSearchQuery) -> SearchResponse:
        start = time.perf_counter()

        logger.info("Consulta recibida: %s", query.text)

        hits = self._store.search(query.text, top_k=query.max_results or self._top_k)

        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            "Búsqueda completada en %.1fms — %d resultados",
            elapsed,
            len(hits),
        )

        results = []
        for idx, hit in enumerate(hits):
            product = CatalogProduct(
                reference=hit.reference,
                name=hit.name,
                description=hit.description,
                category=hit.category,
                subcategory=hit.subcategory,
                price=hit.price,
                currency=hit.currency,
                material=hit.materials,
                colors=hit.colors,
                eco_friendly="eco" in hit.commercial_tags or "ecologico" in hit.category.lower(),
                personalizable="personalizable" in hit.commercial_tags,
                image_url=hit.thumbnail_url or None,
                detail_url=hit.detail_url or None,
                perceived_value_level=hit.perceived_value_level,
                tags=list(set(
                    hit.commercial_tags + hit.occasion_tags + hit.audience_tags
                )),
                score=hit.score,
            )

            explanation = SearchExplanation(
                reason=f"Similitud semántica: {hit.score:.2f}",
                source="chroma",
            )

            results.append(
                CatalogSearchResult(
                    product=product,
                    relevance_score=hit.score,
                    rank=idx + 1,
                    explanation=explanation,
                )
            )

        return SearchResponse(
            query=query.text,
            results=results,
            total_results=len(results),
            metadata=SearchMetadata(
                processing_time_ms=elapsed,
                total_candidates=len(hits),
                results_returned=len(results),
                embedding_used=True,
                keyword_used=False,
            ),
        )
