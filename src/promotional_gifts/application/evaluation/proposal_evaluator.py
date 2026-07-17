from dataclasses import dataclass, field
from typing import Callable, List, Union

from ...domain.entities.commercial_proposal import CommercialProposal
from ...domain.entities.commercial_intent import CommercialIntent
from ...domain.entities.proposal_set import ProposalSet


@dataclass
class EvaluationCase:
    name: str
    query: str
    must_contain_keywords: List[str] = field(default_factory=list)
    any_of_keywords: List[str] = field(default_factory=list)
    must_not_contain_keywords: List[str] = field(default_factory=list)
    min_products: int = 1
    max_cost_per_unit: float = None


@dataclass
class EvaluationResult:
    name: str
    query: str
    passed: bool
    details: List[str]


class ProposalEvaluator:
    def __init__(self, cases: List[EvaluationCase]) -> None:
        self.cases = cases

    def evaluate(
        self,
        generate: Callable[[str], Union[List[CommercialProposal], ProposalSet]],
    ) -> List[EvaluationResult]:
        results: List[EvaluationResult] = []
        for case in self.cases:
            proposals = self._normalize_proposals(generate(case.query))
            details, passed = self._check(case, proposals)
            results.append(
                EvaluationResult(case.name, case.query, passed, details)
            )
        return results

    def _normalize_proposals(
        self, result: Union[List[CommercialProposal], ProposalSet]
    ) -> List[CommercialProposal]:
        if isinstance(result, ProposalSet):
            return result.proposals
        return result

    def _check(
        self, case: EvaluationCase, proposals: List[CommercialProposal]
    ) -> tuple:
        details: List[str] = []
        passed = True

        if not proposals:
            return ["No se generaron propuestas."], False

        all_items = [item for p in proposals for item in p.items]
        if len(all_items) < case.min_products:
            details.append(
                f"Productos insuficientes: {len(all_items)} < {case.min_products}"
            )
            passed = False

        names = " ".join(i.name.lower() for i in all_items)
        for kw in case.must_contain_keywords:
            if kw.lower() not in names:
                details.append(f"Falta categoría esperada: {kw}")
                passed = False

        if case.any_of_keywords and not any(
            kw.lower() in names for kw in case.any_of_keywords
        ):
            details.append(
                "No aparece ninguna categoría esperada: "
                + ", ".join(case.any_of_keywords)
            )
            passed = False

        for kw in case.must_not_contain_keywords:
            if kw.lower() in names:
                details.append(f"Aparece categoría prohibida: {kw}")
                passed = False

        if case.max_cost_per_unit is not None:
            over = [
                i.name
                for i in all_items
                if i.unit_price.amount > case.max_cost_per_unit
            ]
            if over:
                details.append(
                    f"{len(over)} productos superan el costo por unidad."
                )
                passed = False

        if passed:
            details.append(
                f"OK: {len(proposals)} propuestas, {len(all_items)} productos."
            )
        return details, passed


DEFAULT_CASES: List[EvaluationCase] = [
    EvaluationCase(
        name="Cumpleaños 3800 x 25000",
        query="Necesito 3800 regalos de cumpleaños con un presupuesto máximo de 25000 COP por unidad",
        any_of_keywords=["mug", "libreta", "termo", "agenda", "bolsa", "taza"],
        must_not_contain_keywords=["medico", "industrial", "materia prima"],
        min_products=2,
        max_cost_per_unit=25000,
    ),
    EvaluationCase(
        name="Navidad eco 500 x 18000",
        query="Necesito 500 regalos de navidad eco con presupuesto máximo de 18000 COP por unidad",
        must_not_contain_keywords=["medico", "industrial", "materia prima"],
        min_products=2,
        max_cost_per_unit=18000,
    ),
]
