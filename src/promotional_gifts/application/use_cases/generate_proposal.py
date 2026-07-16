from typing import List, Tuple

from ...domain.entities.commercial_intent import CommercialIntent
from ...domain.entities.commercial_proposal import CommercialProposal
from ...domain.entities.product_knowledge import ProductKnowledge
from ...domain.ports.intent_analyzer_port import IntentAnalyzerPort
from ...domain.ports.vector_store_port import VectorStorePort
from ...domain.services.budget_optimizer import BudgetOptimizer
from ...domain.services.product_selector import ProductSelector
from ...domain.services.pricing_engine import PricingEngine
from ...domain.services.proposal_builder import ProposalBuilder
from ...domain.services.proposal_ranker import ProposalRanker


class GenerateProposalUseCase:
    def __init__(
        self,
        intent_analyzer: IntentAnalyzerPort,
        vector_store: VectorStorePort,
        top_k: int = 50,
    ) -> None:
        self.intent_analyzer = intent_analyzer
        self.vector_store = vector_store
        self.top_k = top_k
        self.budget_optimizer = BudgetOptimizer()
        self.product_selector = ProductSelector()
        self.pricing_engine = PricingEngine()
        self.proposal_builder = ProposalBuilder()
        self.proposal_ranker = ProposalRanker()

    def execute(self, text: str) -> List[CommercialProposal]:
        intent = self.intent_analyzer.analyze(text)
        candidates = self._retrieve(intent)
        plan = self.budget_optimizer.optimize(intent)
        scored = self.product_selector.select(candidates, intent, plan)

        raw_proposals = self.proposal_builder.build(scored, intent, plan)
        priced: List[CommercialProposal] = []
        for proposal in raw_proposals:
            priced.append(self.pricing_engine.price(proposal, plan))

        ranked = self.proposal_ranker.rank(priced, intent, plan)
        return ranked

    def _retrieve(
        self, intent: CommercialIntent
    ) -> List[Tuple[ProductKnowledge, float]]:
        query = self._build_query(intent)
        return self.vector_store.search(query=query, top_k=self.top_k)

    def _build_query(self, intent: CommercialIntent) -> str:
        tokens = []
        if intent.occasion:
            tokens.append(intent.occasion)
        if intent.target_audience:
            tokens.append(intent.target_audience)
        if intent.eco:
            tokens.append("eco sostenible")
        if intent.personalizable:
            tokens.append("personalizable logo")
        tokens.append("regalo promocional")
        return " ".join(tokens)
