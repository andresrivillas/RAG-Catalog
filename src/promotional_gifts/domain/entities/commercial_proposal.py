from dataclasses import dataclass, field
from typing import List

from ..value_objects.money import Money


@dataclass
class ProposalItem:
    reference: str
    name: str
    unit_price: Money
    quantity: int

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

    @property
    def units(self) -> int:
        return sum(item.quantity for item in self.items)
