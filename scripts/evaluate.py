from promotional_gifts.container import (
    IntentAnalyzer,
    build_vector_store,
    settings,
)
from promotional_gifts.application.use_cases.generate_proposal import (
    GenerateProposalUseCase,
)
from promotional_gifts.application.evaluation.proposal_evaluator import (
    ProposalEvaluator,
    DEFAULT_CASES,
)


def main() -> None:
    use_case = GenerateProposalUseCase(
        intent_analyzer=IntentAnalyzer(),
        vector_store=build_vector_store(),
        top_k=settings.top_k * 10,
        negative_keywords=settings.negative_categories,
    )
    evaluator = ProposalEvaluator(DEFAULT_CASES)
    results = evaluator.evaluate(use_case.execute)

    passed = 0
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}")
        for detail in result.details:
            print(f"   - {detail}")
        if result.passed:
            passed += 1

    print(f"\nResumen: {passed}/{len(results)} casos exitosos")


if __name__ == "__main__":
    main()
