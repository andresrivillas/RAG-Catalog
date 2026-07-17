from .....shared.dictionaries.product_families import is_product_in_family, get_family_key
from ..context import SearchContext


class FamilyBoostStage:
    def execute(self, ctx: SearchContext) -> None:
        if (
            ctx.intent is None
            or ctx.structured_query is None
            or ctx.intent.intent_type != "PRODUCT_FAMILY"
            or not ctx.intent.detected_product_family
            or ctx.response is None
        ):
            return

        family_key = get_family_key(ctx.structured_query.detected_product_types)
        if not family_key:
            return

        family_matches = []
        others = []
        for r in ctx.response.results:
            if is_product_in_family(r.product.name, r.product.category, family_key):
                family_matches.append(r)
            else:
                others.append(r)

        ctx.response.results = family_matches + others
        ctx.response.total_results = len(ctx.response.results)
        for idx, r in enumerate(ctx.response.results):
            r.rank = idx + 1
