from statistics import median
from typing import List

from ....domain.entities.commercial_proposal import CommercialProposal
from ....domain.services.diversity_engine import DiversityEngine
from ....domain.services.kit_builder import KitBuilder, KitBuildConfig
from ....domain.services.proposal_builder import _BASE_STRATEGIES
from ....domain.services.product_selector import ScoredProduct
from ..context import ProposalContext


def _item_from_line(line):
    from ....domain.entities.commercial_proposal import ProposalItem
    return ProposalItem(
        reference=line.product.reference,
        name=line.product.name,
        unit_price=line.product.price,
        quantity=0,
        role=line.role,
        selection_reason=line.reason,
        decision_trace=line.trace,
        thumbnail_url=line.product.thumbnail_url or line.product.image_url,
        detail_url=line.product.detail_url or line.product.url,
        category=line.product.category,
        materials=line.product.materials,
        colors=line.product.colors,
        capacity=line.product.capacity,
        customization=line.product.customization,
        eco="eco" in (line.product.commercial_tags or []),
        personalizable="personalizable" in (line.product.commercial_tags or []),
        perceived_value_level=line.product.perceived_value_level,
    )


class DiversityStage:
    def __init__(self, builder_config) -> None:
        self._builder_config = builder_config
        self._diversity = DiversityEngine(similarity_threshold=0.55)

    def execute(self, ctx: ProposalContext) -> None:
        if ctx.proposal_set is None or not ctx.proposal_set.proposals:
            return
        max_iterations = 3
        for _ in range(max_iterations):
            scores = [p.score for p in ctx.proposal_set.proposals]
            need = self._diversity.needs_rebuild(ctx.proposal_set.proposals, scores)
            if need is None:
                break
            worst_idx, _, sim = need
            blacklist = self._diversity.blacklist_from(ctx.proposal_set.proposals, worst_idx)
            rebuilt = self._rebuild_one(ctx, worst_idx, blacklist)
            ctx.proposal_set.proposals[worst_idx] = rebuilt
            self._price_and_evaluate(ctx)

    def _rebuild_one(self, ctx: ProposalContext, worst_idx: int, blacklist: set) -> CommercialProposal:
        strategy = _BASE_STRATEGIES[worst_idx % len(_BASE_STRATEGIES)]
        available = [sp for sp in ctx.scored_products if sp.product.reference not in blacklist]
        ranked = strategy.rerank(available, ctx.intent, ctx.plan)
        price_median = median([sp.product.price.amount for sp in ranked]) if ranked else 0.0
        kit_builder = KitBuilder(
            KitBuildConfig(
                num_kits=1,
                min_lines=self._builder_config.min_lines,
                max_lines=self._builder_config.max_lines,
                price_median=price_median,
                mode=strategy.generation_mode,
                concept=strategy.label,
            )
        )
        kits = kit_builder.build(ctx.intent, ranked, ctx.plan)
        proposal = CommercialProposal(name="", score=0.0)
        proposal.generation_mode = strategy.generation_mode.value
        if kits:
            for line in kits[0]:
                item = _item_from_line(line)
                item.quantity = ctx.plan.quantity if ctx.plan else 0
                proposal.items.append(item)
        return proposal

    def _price_and_evaluate(self, ctx: ProposalContext) -> None:
        from ....domain.services.pricing_engine import PricingEngine
        from ....domain.services.evaluation.proposal_evaluation_engine import ProposalEvaluationEngine
        pricing = PricingEngine()
        evaluation = ProposalEvaluationEngine()
        for proposal in ctx.proposal_set.proposals:
            pricing.price(proposal, ctx.plan)
            card = evaluation.evaluate(proposal, ctx.intent, ctx.plan)
            proposal.score_card = card
            proposal.score = card.overall_score
        proposals = ctx.proposal_set.proposals
        proposals.sort(key=lambda p: p.score, reverse=True)
        for index, proposal in enumerate(proposals, start=1):
            proposal.name = f"PROPUESTA {index}"
