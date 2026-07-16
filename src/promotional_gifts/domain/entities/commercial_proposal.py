from dataclasses import dataclass, field
from typing import List, Optional

from ..services.decision_trace import DecisionTrace
from ..services.evaluation.proposal_score_card import ProposalScoreCard
from ..value_objects.money import Money


@dataclass
class ProposalItem:
    reference: str
    name: str
    unit_price: Money
    quantity: int
    role: str = ""
    selection_reason: str = ""
    decision_trace: Optional[DecisionTrace] = None

    @property
    def subtotal(self) -> Money:
        return Money(
            amount=self.unit_price.amount * self.quantity,
            currency=self.unit_price.currency,
        )


@dataclass
class CommercialProposal:
    name: str
    score: float
    items: List[ProposalItem] = field(default_factory=list)
    total_cost: Money = field(default_factory=lambda: Money(0.0))
    per_unit_cost: Money = field(default_factory=lambda: Money(0.0))
    warnings: List[str] = field(default_factory=list)
    occasion: str = ""
    target_audience: str = ""
    commercial_description: str = ""
    proposal_id: str = ""
    version: int = 1
    parent_version: int = 0
    refined: bool = False
    refinements: List[str] = field(default_factory=list)
    score_card: Optional[ProposalScoreCard] = None

    def clone_as_refinement(self) -> "CommercialProposal":
        new = CommercialProposal(
            name=self.name,
            score=self.score,
            items=[item for item in self.items],
            total_cost=self.total_cost,
            per_unit_cost=self.per_unit_cost,
            warnings=[w for w in self.warnings],
            occasion=self.occasion,
            target_audience=self.target_audience,
            commercial_description=self.commercial_description,
            proposal_id=self.proposal_id,
            version=self.version + 1,
            parent_version=self.version,
            refined=True,
        )
        return new

    @property
    def units(self) -> int:
        return sum(item.quantity for item in self.items)
