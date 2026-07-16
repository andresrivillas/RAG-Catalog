from pathlib import Path

from config.settings import settings

from .domain.entities.product_knowledge import ProductKnowledge
from .domain.ports.embedding_port import EmbeddingPort
from .domain.ports.vector_store_port import VectorStorePort
from .application.intent_analyzer import IntentAnalyzer
from .application.prompt.commercial_writer import CommercialWriter
from .application.prompt.prompt_context_builder import PromptContextBuilder
from .application.prompt.prompt_loader import PromptLoader
from .application.use_cases.generate_proposal import GenerateProposalUseCase
from .domain.ports.llm_port import LLMPort
from .infrastructure.embeddings.sentence_transformer_embedding import (
    SentenceTransformerEmbedding,
)
from .infrastructure.ingestion.excel_source import ExcelIngestionSource
from .infrastructure.llm.ollama_llm import OllamaLLM
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


def build_llm() -> LLMPort:
    return OllamaLLM(
        host=settings.ollama_host,
        top_p=settings.top_p,
        max_tokens=settings.max_tokens,
    )


def build_commercial_writer() -> CommercialWriter:
    return CommercialWriter(
        llm=build_llm(),
        prompt_loader=PromptLoader(settings.prompts_path),
        context_builder=PromptContextBuilder(),
    )


def build_generate_proposal_use_case() -> GenerateProposalUseCase:
    return GenerateProposalUseCase(
        intent_analyzer=IntentAnalyzer(),
        vector_store=build_vector_store(),
        top_k=settings.top_k * 10,
        commercial_writer=build_commercial_writer(),
        llm_model=settings.ollama_model,
        llm_temperature=settings.ollama_temperature,
    )
