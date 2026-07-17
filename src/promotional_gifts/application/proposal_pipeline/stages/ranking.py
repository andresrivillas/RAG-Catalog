from ..context import ProposalContext


class RankingStage:
    def execute(self, ctx: ProposalContext) -> None:
        if ctx.proposal_set is None:
            return
        proposals = ctx.proposal_set.proposals
        proposals.sort(key=lambda p: p.score, reverse=True)
        for index, proposal in enumerate(proposals, start=1):
            proposal.name = f"PROPUESTA {index}"
