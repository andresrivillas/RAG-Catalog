from typing import List

from ..entities.commercial_intent import CommercialIntent
from ..entities.commercial_proposal import CommercialProposal
from ..services.budget_plan import BudgetPlan


class ProposalRanker:
    def rank(
        self,
        proposals: List[CommercialProposal],
        intent: CommercialIntent,
        plan: BudgetPlan,
    ) -> List[CommercialProposal]:
        for proposal in proposals:
            proposal.score = self._score(proposal, plan)

        proposals.sort(key=lambda p: p.score, reverse=True)

        for index, proposal in enumerate(proposals, start=1):
            proposal.name = f"PROPUESTA {index}"
        return proposals

    def _score(
        self, proposal: CommercialProposal, plan: BudgetPlan
    ) -> float:
        if plan.spendable_budget <= 0:
            return 0.0
        used_ratio = proposal.total_cost.amount / plan.spendable_budget
        budget_score = min(used_ratio, 1.0) * 50

        categories = set()
        for item in proposal.items:
            categories.add(item.name.split()[0])
        diversity_score = min(len(proposal.items), 5) / 5 * 25

        value_score = 0.0
        if proposal.items:
            value_score = 25

        return budget_score + diversity_score + value_score
