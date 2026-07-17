from ..context import ProposalContext


class FinalValidationStage:
    def execute(self, ctx: ProposalContext) -> None:
        if ctx.proposal_set is None:
            return
        warnings: list[str] = []
        for proposal in ctx.proposal_set.proposals:
            if ctx.plan and ctx.plan.spendable_budget > 0 and proposal.total_cost.amount > ctx.plan.spendable_budget * 1.05:
                warnings.append(
                    f"{proposal.name}: supera el presupuesto usable en "
                    f"{(proposal.total_cost.amount / ctx.plan.spendable_budget - 1) * 100:.0f}%."
                )
            if len(proposal.items) < 3:
                warnings.append(
                    f"{proposal.name}: kit con pocos productos ({len(proposal.items)})."
                )
        if ctx.proposal_set.statistics is not None:
            ctx.proposal_set.statistics.warnings.extend(warnings)
