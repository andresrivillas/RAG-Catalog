from typing import List

from ....domain.services.proposal_builder import ProposalBuilder
from ..context import ProposalContext


class StatisticsStage:
    def __init__(self, builder: ProposalBuilder) -> None:
        self._builder = builder

    def execute(self, ctx: ProposalContext) -> None:
        if ctx.proposal_set is None:
            return
        ctx.proposal_set.statistics = self._builder._compute_statistics(ctx.proposal_set)
        if ctx.proposal_set.statistics:
            ctx.proposal_set.reused_products = (
                ctx.proposal_set.statistics.reused_references
            )

        obs = self._global_observations(ctx)
        ctx.proposal_set.global_observations = obs

    def _global_observations(self, ctx: ProposalContext) -> List[str]:
        obs: List[str] = []
        if ctx.proposal_set is None:
            return obs
        stats = ctx.proposal_set.statistics
        if stats is None:
            return obs
        obs.append(
            f"Set global de {stats.total_proposals} propuestas con "
            f"{stats.category_coverage} categorias distintas cubiertas."
        )
        if stats.reused_products:
            obs.append(
                f"{stats.reused_products} producto(s) reutilizado(s) entre propuestas: "
                f"{', '.join(stats.reused_references)}."
            )
        if stats.shared_product_count:
            obs.append(
                f"{stats.shared_product_count} producto(s) compartido(s) en todas las propuestas: "
                f"{', '.join(stats.shared_references)}."
            )
        obs.append(f"Similitud maxima entre propuestas: {stats.max_similarity:.0%}.")
        return obs
