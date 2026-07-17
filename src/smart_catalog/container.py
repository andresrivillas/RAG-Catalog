from pathlib import Path

from config.settings import settings

from .domain.ports.catalog_search_service import CatalogSearchService
from .domain.ports.embedding_search_service import EmbeddingSearchService
from .domain.ports.keyword_search_service import KeywordSearchService
from .domain.ports.product_repository import ProductRepository
from .domain.ports.metadata_resolver import MetadataResolver
from .domain.ports.search_ranking_service import SearchRankingService as SearchRankingPort
from .domain.ports.history_repository import HistoryRepository
from .infrastructure.services.mock_catalog_search_service import (
    MockCatalogSearchService,
)
from .infrastructure.services.chroma_catalog_search_service import (
    ChromaCatalogSearchService,
)
from .infrastructure.services.mock_embedding_search_service import (
    MockEmbeddingSearchService,
)
from .infrastructure.services.mock_keyword_search_service import (
    MockKeywordSearchService,
)
from .infrastructure.services.mock_product_repository import MockProductRepository
from .infrastructure.services.mock_metadata_resolver import MockMetadataResolver
from .infrastructure.services.mock_search_ranking_service import (
    MockSearchRankingService,
)
from .infrastructure.services.mock_history_repository import MockHistoryRepository
from .infrastructure.vector_store.chroma_catalog_store import ChromaCatalogStore
from .presentation.slices.search_catalog.service import SearchCatalogService
from .presentation.slices.search_ranking.service import SearchRankingService
from .presentation.slices.search_ranking.engine import (
    SearchRankingEngine,
    RankingWeights,
)
from .presentation.slices.semantic_query_expansion.service import (
    SemanticQueryExpansionService,
)
from .presentation.slices.semantic_query_expansion.engine import (
    SemanticQueryExpansionEngine,
)
from .presentation.slices.search_explanation.service import (
    SearchExplanationService,
)
from .presentation.slices.search_explanation.engine import (
    SearchExplanationEngine,
)
from .presentation.slices.intent_resolution.service import (
    IntentResolutionService,
)
from .presentation.slices.intent_resolution.engine import (
    IntentResolutionEngine,
)


def build_catalog_search_service() -> CatalogSearchService:
    return build_chroma_catalog_search_service()


def build_chroma_catalog_search_service() -> ChromaCatalogSearchService:
    return ChromaCatalogSearchService(
        store=build_chroma_store(),
        top_k=30,
    )


def build_chroma_store() -> ChromaCatalogStore:
    return ChromaCatalogStore(
        persist_directory=settings.chroma_dir,
        collection_name=settings.collection_name,
    )


def build_search_catalog_service() -> SearchCatalogService:
    return SearchCatalogService(
        search_service=build_chroma_catalog_search_service(),
        ranking_service=build_search_ranking_service(),
        expansion_service=build_semantic_query_expansion_service(),
        explanation_service=build_search_explanation_service(),
        intent_service=build_intent_resolution_service(),
    )


def build_search_ranking_service() -> SearchRankingService:
    return SearchRankingService(
        engine=SearchRankingEngine(weights=RankingWeights()),
    )


def build_semantic_query_expansion_service() -> SemanticQueryExpansionService:
    return SemanticQueryExpansionService(
        engine=SemanticQueryExpansionEngine(),
    )


def build_search_explanation_service() -> SearchExplanationService:
    return SearchExplanationService(
        engine=SearchExplanationEngine(),
    )


def build_intent_resolution_service() -> IntentResolutionService:
    return IntentResolutionService(
        engine=IntentResolutionEngine(),
    )


def build_embedding_search_service() -> EmbeddingSearchService:
    return MockEmbeddingSearchService()


def build_keyword_search_service() -> KeywordSearchService:
    return MockKeywordSearchService()


def build_product_repository() -> ProductRepository:
    return MockProductRepository()


def build_metadata_resolver() -> MetadataResolver:
    return MockMetadataResolver()


def build_search_ranking_port() -> SearchRankingPort:
    return MockSearchRankingService()


def build_history_repository() -> HistoryRepository:
    return MockHistoryRepository()
