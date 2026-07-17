from typing import List, Optional

from ...domain.entities.commercial_intent import CommercialIntent
from ...domain.entities.proposal_set import ProposalSet
from ...domain.ports.intent_analyzer_port import IntentAnalyzerPort
from ...domain.ports.vector_store_port import VectorStorePort
from ...domain.ports.llm_port import LLMPort
from ...domain.services.generation_mode import GenerationMode
from ...domain.services.workspace.proposal_workspace import ProposalWorkspace
from ..prompt.commercial_writer import CommercialWriter
from ..proposal_pipeline.pipeline import ProposalPipeline


class GenerateProposalUseCase:
    def __init__(
        self,
        intent_analyzer: IntentAnalyzerPort,
        vector_store: VectorStorePort,
        top_k: int = 50,
        commercial_writer: Optional[CommercialWriter] = None,
        llm_model: str = "llama3.2",
        llm_temperature: float = 0.3,
        negative_keywords: List[str] = None,
        workspace: ProposalWorkspace = None,
        mode: GenerationMode = None,
    ) -> None:
        self._pipeline = ProposalPipeline(
            intent_analyzer=intent_analyzer,
            vector_store=vector_store,
            top_k=top_k,
            negative_keywords=negative_keywords or [],
            mode=mode or GenerationMode.BALANCED,
            commercial_writer=commercial_writer,
            llm_model=llm_model,
            llm_temperature=llm_temperature,
            workspace=workspace,
        )

    def execute(
        self,
        text: str,
        intent: Optional[CommercialIntent] = None,
        plan=None,
    ) -> ProposalSet:
        return self._pipeline.run(
            text=text,
            intent=intent,
            plan=plan,
        )
