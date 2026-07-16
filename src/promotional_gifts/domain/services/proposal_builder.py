from dataclasses import dataclass
from statistics import median
from typing import List

from ..entities.commercial_intent import CommercialIntent
from ..entities.commercial_proposal import CommercialProposal, ProposalItem
from ..entities.product_knowledge import ProductKnowledge
from ..services.budget_plan import BudgetPlan
from ..services.kit_builder import KitBuilder, KitBuildConfig
from ..services.product_selector import ScoredProduct


@dataclass
class BuildConfig:
    num_proposals: int = 3
    min_lines: int = 2
    max_lines: int = 5
    min_units_per_item: int = 1


class ProposalBuilder:
    def __init__(self, config: BuildConfig = None) -> None:
        self.config = config or BuildConfig()

    def build(
        self,
        scored: List[ScoredProduct],
        intent: CommercialIntent,
        plan: BudgetPlan,
    ) -> List[CommercialProposal]:
        products: List[ProductKnowledge] = [sp.product for sp in scored]
        if not products:
            return []

        price_median = median([p.price.amount for p in products]) if products else 0.0

        kit_builder = KitBuilder(
            KitBuildConfig(
                num_kits=self.config.num_proposals,
                min_lines=self.config.min_lines,
                max_lines=self.config.max_lines,
                price_median=price_median,
            )
        )

        kits = kit_builder.build(intent, scored, plan)
        proposals: List[CommercialProposal] = []
        for kit in kits:
            proposal = CommercialProposal(name="", score=0.0)
            used_refs = set()
            for line in kit:
                if line.product.reference in used_refs:
                    continue
                used_refs.add(line.product.reference)
                proposal.items.append(
                    ProposalItem(
                        reference=line.product.reference,
                        name=line.product.name,
                        unit_price=line.product.price,
                        quantity=plan.quantity,
                        role=line.role,
                        selection_reason=line.reason,
                        decision_trace=line.trace,
                    )
                )
            if proposal.items:
                proposals.append(proposal)
        return proposals
