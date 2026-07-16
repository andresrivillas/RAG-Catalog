from dataclasses import dataclass
from typing import List

from ..entities.commercial_intent import CommercialIntent
from ..entities.commercial_proposal import CommercialProposal, ProposalItem
from ..services.budget_plan import BudgetPlan
from ..services.product_selector import ScoredProduct

CATEGORY_KEYWORDS = {
    "escritura": ["lapiz", "boligrafo", "bolígrafo", "resaltador", "pluma", "portaminas"],
    "bolsos": ["bolsa", "mochila", "cartera", "estuche"],
    "hogar": ["taza", "mug", "termo", "vaso", "plat", "copa"],
    "tecnologia": ["usb", "cargador", "auricular", "altavoz", "speaker", "power bank"],
    "oficina": ["libreta", "cuaderno", "carpeta", "agenda", "notas"],
    "viaje": ["paraguas", "maleta", "neceser", "viaje"],
}


def derive_category(product) -> str:
    text = f"{product.name} {product.description}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return "otros"


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
        proposals: List[CommercialProposal] = []
        used_references: set = set()

        anchors = scored[: self.config.num_proposals * 2] or scored
        for i in range(self.config.num_proposals):
            if i >= len(anchors):
                break
            anchor = anchors[i]
            proposal = self._build_one(
                anchor, scored, intent, plan, used_references
            )
            if proposal and proposal.items:
                proposals.append(proposal)
        return proposals

    def _build_one(
        self,
        anchor: ScoredProduct,
        scored: List[ScoredProduct],
        intent: CommercialIntent,
        plan: BudgetPlan,
        used_references: set,
    ) -> CommercialProposal:
        proposal = CommercialProposal(
            name=f"Propuesta {derive_category(anchor.product).title()}",
            score=0.0,
        )
        remaining_budget = plan.spendable_budget
        categories_used: set = set()

        items = [anchor] + [
            s for s in scored if s.product.reference != anchor.product.reference
        ]

        for sp in items:
            if len(proposal.items) >= self.config.max_lines:
                break
            ref = sp.product.reference
            if ref in used_references:
                continue
            unit = sp.product.price.amount
            max_units = int(remaining_budget // unit) if unit > 0 else 0
            if max_units < self.config.min_units_per_item:
                continue

            units = max(self.config.min_units_per_item, max_units)
            if units > plan.quantity:
                units = plan.quantity

            category = derive_category(sp.product)
            if (
                category in categories_used
                and len(proposal.items) >= 1
                and len(categories_used) >= 1
            ):
                continue

            proposal.items.append(
                ProposalItem(
                    reference=ref,
                    name=sp.product.name,
                    unit_price=sp.product.price,
                    quantity=units,
                )
            )
            used_references.add(ref)
            categories_used.add(category)
            remaining_budget -= unit * units

            if len(proposal.items) >= self.config.min_lines and remaining_budget <= 0:
                break

        return proposal
