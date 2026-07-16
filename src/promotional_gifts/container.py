from pathlib import Path

from config.settings import settings

from .domain.entities.product_knowledge import ProductKnowledge
from .domain.ports.embedding_port import EmbeddingPort
from .domain.ports.vector_store_port import VectorStorePort
from .application.intent_analyzer import IntentAnalyzer
from .application.use_cases.generate_proposal import GenerateProposalUseCase
from .infrastructure.embeddings.sentence_transformer_embedding import (
    SentenceTransformerEmbedding,
)
from .infrastructure.ingestion.excel_source import ExcelIngestionSource
from .infrastructure.vector_stores.chroma_vector_store import ChromaVectorStore
from .knowledge.store.knowledge_indexer import KnowledgeIndexer
from .knowledge.transform.embedding_builder import EmbeddingBuilder
from .knowledge.transform.metadata_builder import MetadataBuilder
from .knowledge.transform.product_cleaner import ProductCleaner


def build_embedding_port() -> EmbeddingPort:
    return SentenceTransformerEmbedding(model_name=settings.embedding_model)


def build_vector_store() -> VectorStorePort:
    return ChromaVectorStore(
        persist_directory=settings.chroma_dir,
        collection_name=settings.collection_name,
    )


def build_ingestion_source() -> ExcelIngestionSource:
    return ExcelIngestionSource(catalog_path=settings.catalog_path)


def build_knowledge_indexer() -> KnowledgeIndexer:
    embedding_port = build_embedding_port()
    return KnowledgeIndexer(
        cleaner=ProductCleaner(),
        metadata_builder=MetadataBuilder(),
        embedding_builder=EmbeddingBuilder(embedding_port=embedding_port),
        vector_store=build_vector_store(),
    )


def build_generate_proposal_use_case() -> GenerateProposalUseCase:
    return GenerateProposalUseCase(
        intent_analyzer=IntentAnalyzer(),
        vector_store=build_vector_store(),
        top_k=settings.top_k * 10,
    )
