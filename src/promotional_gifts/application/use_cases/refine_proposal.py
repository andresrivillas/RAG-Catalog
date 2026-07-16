from typing import List, Optional, Tuple

from ...domain.entities.commercial_intent import CommercialIntent
from ...domain.entities.commercial_proposal import CommercialProposal
from ...domain.ports.intent_analyzer_port import IntentAnalyzerPort
from ...domain.ports.vector_store_port import VectorStorePort
from ...domain.services.budget_optimizer import BudgetOptimizer
from ...domain.services.commercial_scorer import CommercialScorer
from ...domain.services.negative_filter import NegativeFilter
from ...domain.services.occasion_matcher import OccasionMatcher
from ...domain.services.pricing_engine import PricingEngine
from ..prompt.commercial_writer import CommercialWriter
from ..prompt.prompt_context_builder import PromptContextBuilder
from ..refinement.refinement_analyzer import RefinementAnalyzer
from ..refinement.proposal_refinement_engine import (
    ProposalRefinementEngine,
    RefinementLogEntry,
)


class RefineProposalUseCase:
    def __init__(
        self,
        intent_analyzer: IntentAnalyzerPort,
        vector_store: VectorStorePort,
        top_k: int = 50,
        commercial_writer: Optional[CommercialWriter] = None,
        llm_model: str = "llama3.2",
        llm_temperature: float = 0.3,
        negative_keywords: List[str] = None,
    ) -> None:
        self.intent_analyzer = intent_analyzer
        self.refinement_analyzer = RefinementAnalyzer()
        self.vector_store = vector_store
        self.commercial_writer = commercial_writer
        self._llm_model = llm_model
        self._llm_temperature = llm_temperature
        self.budget_optimizer = BudgetOptimizer()
        self.engine = ProposalRefinementEngine(
            vector_store=vector_store,
            occasion_matcher=OccasionMatcher(),
            commercial_scorer=CommercialScorer(),
            negative_filter=NegativeFilter(negative_keywords or []),
            pricing_engine=PricingEngine(),
            top_k=top_k,
            negative_keywords=negative_keywords,
        )

    def execute(
        self,
        proposal: CommercialProposal,
        instruction: str,
        original_intent: Optional[CommercialIntent] = None,
        original_plan=None,
    ) -> Tuple[CommercialProposal, List[RefinementLogEntry], str]:
        request = self.refinement_analyzer.analyze(instruction)
        intent = original_intent or (
            self.intent_analyzer.analyze(instruction) if self.intent_analyzer else None
        )
        plan = original_plan or (
            self.budget_optimizer.optimize(intent) if intent else None
        )

        new_proposal, log = self.engine.refine(proposal, request, intent, plan)

        refinement_context = PromptContextBuilder().build_refinement(
            new_proposal, proposal, log
        )
        new_proposal.refined = True
        new_proposal.refinements.append(f"v{proposal.version} -> v{new_proposal.version}: {instruction}")

        if self.commercial_writer:
            new_proposal.commercial_description = self.commercial_writer.write(
                new_proposal,
                model=self._llm_model,
                temperature=self._llm_temperature,
                refinement_context=refinement_context,
            )
        return new_proposal, log, request.action
