from ....domain.services.proposal_builder import ProposalBuilder, BuildConfig
from ..context import ProposalContext


class ProposalBuildingStage:
    def __init__(self, builder: ProposalBuilder) -> None:
        self._builder = builder

    def execute(self, ctx: ProposalContext) -> None:
        ctx.proposal_set = self._builder.build_set(ctx.scored_products, ctx.intent, ctx.plan)
