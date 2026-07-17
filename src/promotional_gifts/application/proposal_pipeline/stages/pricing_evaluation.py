from ....domain.services.pricing_engine import PricingEngine
from ....domain.services.evaluation.proposal_evaluation_engine import ProposalEvaluationEngine
from ..context import ProposalContext


class PricingEvaluationStage:
    def __init__(self) -> None:
        self._pricing = PricingEngine()
        self._evaluation = ProposalEvaluationEngine()

    def execute(self, ctx: ProposalContext) -> None:
        if ctx.proposal_set is None:
            return
        for proposal in ctx.proposal_set.proposals:
            self._pricing.price(proposal, ctx.plan)
            card = self._evaluation.evaluate(proposal, ctx.intent, ctx.plan)
            proposal.score_card = card
            proposal.score = card.overall_score
