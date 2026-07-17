from typing import List

from ....domain.entities.commercial_intent import CommercialIntent
from ....domain.services.negative_filter import NegativeFilter
from ....domain.services.occasion_matcher import OccasionMatcher
from ....domain.services.commercial_scorer import CommercialScorer
from ....domain.services.product_selector import ProductSelector, ScoredProduct
from ..context import ProposalContext


class ProductSelectionStage:
    def __init__(self, negative_keywords: List[str]) -> None:
        self._negative_keywords = negative_keywords

    def execute(self, ctx: ProposalContext) -> None:
        relaxed = not ctx.candidates
        pool = ctx.candidates

        selector = ProductSelector(
            occasion_matcher=OccasionMatcher(),
            commercial_scorer=CommercialScorer(),
            negative_filter=NegativeFilter(self._negative_keywords),
        )
        ctx.scored_products = selector.select(pool, ctx.intent, ctx.plan, ctx.mode)

        if not ctx.scored_products:
            relaxed = True
            ctx.scored_products = self._relax_and_select(pool, ctx)

        if relaxed and ctx.scored_products:
            for sp in ctx.scored_products:
                if sp.trace:
                    sp.trace.reason += " (se relajaron restricciones para asegurar propuestas)"

    def _relax_and_select(self, pool, ctx: ProposalContext) -> List[ScoredProduct]:
        relaxed_intent = CommercialIntent(
            raw_text=ctx.intent.raw_text if ctx.intent else "",
            quantity=ctx.intent.quantity if ctx.intent else 0,
            budget_total=ctx.intent.budget_total if ctx.intent else 0,
            budget_per_unit=ctx.intent.budget_per_unit if ctx.intent else 0,
            eco=False,
            personalizable=False,
            packaging_required=False,
            generation_mode=ctx.intent.generation_mode if ctx.intent else "",
            industry=ctx.intent.industry if ctx.intent else "",
            commercial_context_tags=[],
            segment_tags=[],
        )
        relaxed_selector = ProductSelector(
            occasion_matcher=OccasionMatcher(),
            commercial_scorer=CommercialScorer(),
            negative_filter=NegativeFilter([]),
        )
        return relaxed_selector.select(pool, relaxed_intent, ctx.plan, ctx.mode)
