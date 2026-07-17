from ....domain.services.budget_optimizer import BudgetOptimizer
from ..context import ProposalContext


class BudgetOptimizationStage:
    def __init__(self, optimizer: BudgetOptimizer) -> None:
        self._optimizer = optimizer

    def execute(self, ctx: ProposalContext) -> None:
        if ctx.plan is None:
            ctx.plan = self._optimizer.optimize(ctx.intent, ctx.mode)
