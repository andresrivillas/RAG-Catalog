from ..entities.commercial_proposal import CommercialProposal, ProposalItem
from ..services.budget_plan import BudgetPlan
from ..value_objects.money import Money


class PricingEngine:
    def price(
        self, proposal: CommercialProposal, plan: BudgetPlan
    ) -> CommercialProposal:
        total = 0.0
        currency = "COP"
        for item in proposal.items:
            total += item.unit_price.amount * item.quantity
            currency = item.unit_price.currency

        proposal.total_cost = Money(amount=total, currency=currency)
        per_unit = total / plan.quantity if plan.quantity else 0.0
        proposal.per_unit_cost = Money(amount=per_unit, currency=currency)

        if proposal.total_cost.amount > plan.spendable_budget:
            proposal.warnings.append(
                "El costo total supera el presupuesto utilizable."
            )
        return proposal
