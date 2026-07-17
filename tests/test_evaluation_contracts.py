import unittest

from promotional_gifts.application.evaluation.proposal_evaluator import (
    EvaluationCase,
    ProposalEvaluator,
)
from promotional_gifts.domain.entities.commercial_intent import CommercialIntent
from promotional_gifts.domain.entities.commercial_proposal import (
    CommercialProposal,
    ProposalItem,
)
from promotional_gifts.domain.entities.proposal_set import ProposalSet
from promotional_gifts.domain.services.budget_plan import BudgetPlan
from promotional_gifts.domain.value_objects.money import Money


def _proposal(name="PROPUESTA 1"):
    return CommercialProposal(
        name=name,
        score=90.0,
        items=[
            ProposalItem(
                reference="TE-001",
                name="Termo Ejecutivo",
                unit_price=Money(10000),
                quantity=10,
            )
        ],
        per_unit_cost=Money(10000),
        total_cost=Money(100000),
    )


class ProposalEvaluatorContractTest(unittest.TestCase):
    def test_accepts_proposal_set_from_generator(self):
        evaluator = ProposalEvaluator(
            [
                EvaluationCase(
                    name="set",
                    query="Necesito termos",
                    must_contain_keywords=["termo"],
                    min_products=1,
                    max_cost_per_unit=15000,
                )
            ]
        )
        proposal_set = ProposalSet(
            intent=CommercialIntent(raw_text="Necesito termos"),
            budget_plan=BudgetPlan(
                total_budget=150000,
                spendable_budget=150000,
                per_unit_ceiling=15000,
                margin_reserve=0,
                quantity=10,
            ),
            proposal_count=1,
            proposals=[_proposal()],
        )

        results = evaluator.evaluate(lambda _: proposal_set)

        self.assertTrue(results[0].passed)

    def test_keeps_list_generator_compatibility(self):
        evaluator = ProposalEvaluator(
            [EvaluationCase(name="list", query="Necesito termos", min_products=1)]
        )

        results = evaluator.evaluate(lambda _: [_proposal()])

        self.assertTrue(results[0].passed)

    def test_supports_alternative_expected_keywords(self):
        evaluator = ProposalEvaluator(
            [
                EvaluationCase(
                    name="alternatives",
                    query="Necesito regalos",
                    any_of_keywords=["mug", "termo", "agenda"],
                )
            ]
        )

        results = evaluator.evaluate(lambda _: [_proposal()])

        self.assertTrue(results[0].passed)


if __name__ == "__main__":
    unittest.main()
