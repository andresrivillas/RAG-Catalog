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
from .application.use_cases.refine_proposal import RefineProposalUseCase
from .domain.services.evaluation.proposal_evaluation_engine import (
    ProposalEvaluationEngine,
    EvaluationWeights,
)
from .domain.services.workspace.proposal_workspace import ProposalWorkspace
from .infrastructure.persistence.file_proposal_repository import (
    FileProposalRepository,
)
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


def build_cleaner() -> ProductCleaner:
    return ProductCleaner()


def build_enrichment_pipeline():
    from .knowledge.enrichment.catalog_web_scraper import CatalogWebScraper
    from .knowledge.enrichment.knowledge_merger import KnowledgeMerger
    from .knowledge.enrichment.knowledge_enrichment_pipeline import (
        KnowledgeEnrichmentPipeline,
    )
    from .knowledge.enrichment.product_html_parser import ProductHtmlParser

    return KnowledgeEnrichmentPipeline(
        scraper=CatalogWebScraper(),
        parser=ProductHtmlParser(),
        merger=KnowledgeMerger(),
        output_path=settings.enriched_path,
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


def build_generate_proposal_use_case(
    top_k: int = None, llm_model: str = None, mode=None
) -> GenerateProposalUseCase:
    return GenerateProposalUseCase(
        intent_analyzer=IntentAnalyzer(),
        vector_store=build_vector_store(),
        top_k=top_k if top_k is not None else settings.top_k * 10,
        commercial_writer=build_commercial_writer(),
        llm_model=llm_model or settings.ollama_model,
        llm_temperature=settings.ollama_temperature,
        negative_keywords=settings.negative_categories,
        workspace=build_proposal_workspace(),
        mode=mode,
    )


def build_refine_proposal_use_case(
    top_k: int = None, llm_model: str = None
) -> RefineProposalUseCase:
    return RefineProposalUseCase(
        intent_analyzer=IntentAnalyzer(),
        vector_store=build_vector_store(),
        top_k=top_k if top_k is not None else settings.top_k * 10,
        commercial_writer=build_commercial_writer(),
        llm_model=llm_model or settings.ollama_model,
        llm_temperature=settings.ollama_temperature,
        negative_keywords=settings.negative_categories,
        workspace=build_proposal_workspace(),
    )


def build_proposal_repository():
    return FileProposalRepository(settings.proposals_dir)


def build_proposal_workspace() -> ProposalWorkspace:
    return ProposalWorkspace(build_proposal_repository())


def is_catalog_indexed() -> bool:
    try:
        store = build_vector_store()
        return store.count() > 0
    except Exception:
        return False


def is_ollama_available(model: str = None) -> bool:
    try:
        client = OllamaLLM(
            host=settings.ollama_host,
            top_p=settings.top_p,
            max_tokens=settings.max_tokens,
        )
        client.generate(prompt="test", temperature=0.0, model=model or settings.ollama_model)
        return True
    except Exception:
        return False
