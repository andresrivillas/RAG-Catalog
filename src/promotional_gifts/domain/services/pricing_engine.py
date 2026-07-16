from ..entities.commercial_proposal import CommercialProposal, ProposalItem
from ..services.budget_plan import BudgetPlan
from ..value_objects.money import Money


class PricingEngine:
    def price(
        self, proposal: CommercialProposal, plan: BudgetPlan
    ) -> CommercialProposal:
        valid_items: List[ProposalItem] = []
        total = 0.0
        currency = proposal.total_cost.currency or "COP"

        for item in proposal.items:
            price = item.unit_price
            if price is None or price.amount is None or price.amount <= 0:
                proposal.warnings.append(
                    f"Producto {item.reference} sin precio válido; excluido del costo."
                )
                continue
            total += price.amount * item.quantity
            currency = price.currency
            valid_items.append(item)

        proposal.items = valid_items
        proposal.total_cost = Money(amount=total, currency=currency)
        per_unit = total / plan.quantity if plan.quantity else 0.0
        proposal.per_unit_cost = Money(amount=per_unit, currency=currency)

        if plan.spendable_budget > 0 and proposal.total_cost.amount > plan.spendable_budget:
            proposal.warnings.append(
                "El costo total supera el presupuesto utilizable."
            )
        if not valid_items:
            proposal.warnings.append(
                "Ningún producto con precio válido en la propuesta."
            )
        return proposal
