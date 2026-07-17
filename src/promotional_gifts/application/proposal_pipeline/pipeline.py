import logging
from typing import List, Optional

from ...domain.entities.commercial_intent import CommercialIntent
from ...domain.entities.proposal_set import ProposalSet
from ...domain.ports.intent_analyzer_port import IntentAnalyzerPort
from ...domain.ports.vector_store_port import VectorStorePort
from ...domain.services.budget_optimizer import BudgetOptimizer
from ...domain.services.generation_mode import GenerationMode
from ...domain.services.proposal_builder import ProposalBuilder, BuildConfig
from ...domain.services.workspace.proposal_workspace import ProposalWorkspace
from ..prompt.commercial_writer import CommercialWriter
from .context import ProposalContext
from .stages.intent_analysis import IntentAnalysisStage
from .stages.budget_optimization import BudgetOptimizationStage
from .stages.retrieval import RetrievalStage
from .stages.product_selection import ProductSelectionStage
from .stages.proposal_building import ProposalBuildingStage
from .stages.pricing_evaluation import PricingEvaluationStage
from .stages.ranking import RankingStage
from .stages.diversity import DiversityStage
from .stages.statistics import StatisticsStage
from .stages.final_validation import FinalValidationStage
from .stages.llm_writing import LlmWritingStage
from .stages.persistence import PersistenceStage

logger = logging.getLogger("promotional_gifts.pipeline")


class ProposalPipeline:
    def __init__(
        self,
        intent_analyzer: IntentAnalyzerPort,
        vector_store: VectorStorePort,
        top_k: int = 50,
        negative_keywords: Optional[List[str]] = None,
        mode: Optional[GenerationMode] = None,
        commercial_writer: Optional[CommercialWriter] = None,
        llm_model: str = "llama3.2",
        llm_temperature: float = 0.3,
        workspace: Optional[ProposalWorkspace] = None,
    ) -> None:
        nk = negative_keywords or []
        builder = ProposalBuilder(BuildConfig(mode=mode or GenerationMode.BALANCED))

        self._stages = [
            IntentAnalysisStage(intent_analyzer),
            BudgetOptimizationStage(BudgetOptimizer()),
            RetrievalStage(vector_store),
            ProductSelectionStage(nk),
            ProposalBuildingStage(builder),
            PricingEvaluationStage(),
            RankingStage(),
            DiversityStage(builder.config),
            StatisticsStage(builder),
            FinalValidationStage(),
            LlmWritingStage(),
            PersistenceStage(),
        ]
        self._top_k = top_k
        self._commercial_writer = commercial_writer
        self._llm_model = llm_model
        self._llm_temperature = llm_temperature
        self._workspace = workspace

    def run(
        self,
        text: str,
        intent: Optional[CommercialIntent] = None,
        plan=None,
        mode: Optional[GenerationMode] = None,
    ) -> ProposalSet:
        ctx = ProposalContext(
            text=text,
            intent=intent,
            plan=plan,
            mode=mode or GenerationMode.BALANCED,
            top_k=self._top_k,
            commercial_writer=self._commercial_writer,
            llm_model=self._llm_model,
            llm_temperature=self._llm_temperature,
            workspace=self._workspace,
        )

        for stage in self._stages:
            stage.execute(ctx)

        return ctx.proposal_set
