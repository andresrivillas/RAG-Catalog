from typing import List

from ..entities.commercial_intent import CommercialIntent
from ..entities.commercial_proposal import CommercialProposal
from ..services.budget_plan import BudgetPlan
from ..services.evaluation.proposal_evaluation_engine import (
    ProposalEvaluationEngine,
)


class ProposalRanker:
    def __init__(
        self,
        evaluation_engine: ProposalEvaluationEngine = None,
        debug: bool = False,
    ) -> None:
        self.evaluation_engine = evaluation_engine or ProposalEvaluationEngine(
            debug=debug
        )

    def rank(
        self,
        proposals: List[CommercialProposal],
        intent: CommercialIntent,
        plan: BudgetPlan,
    ) -> List[CommercialProposal]:
        for proposal in proposals:
            card = self.evaluation_engine.evaluate(proposal, intent, plan)
            proposal.score_card = card
            proposal.score = card.overall_score

        proposals = self._apply_diversity(proposals)

        proposals.sort(key=lambda p: p.score, reverse=True)

        for index, proposal in enumerate(proposals, start=1):
            proposal.name = f"PROPUESTA {index}"
        return proposals

    def _apply_diversity(
        self, proposals: List[CommercialProposal]
    ) -> List[CommercialProposal]:
        for i, proposal in enumerate(proposals):
            for other in proposals[:i]:
                shared = self._shared_refs(proposal, other)
                if shared:
                    proposal.score -= 8 * shared
        return proposals

    def _shared_refs(
        self, a: CommercialProposal, b: CommercialProposal
    ) -> int:
        refs_a = {item.reference for item in a.items}
        refs_b = {item.reference for item in b.items}
        return len(refs_a & refs_b)
