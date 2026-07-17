import time
from collections import Counter
from typing import Optional

from ..presentation.slices.query_understanding.service import QueryUnderstandingService
from ..container import build_search_catalog_service
from .models import TestCase, DetectorResult, SingleResult, EvaluationSummary
from .metrics import (
    precision_at_k, recall_at_k, mrr, ndcg,
    detector_accuracy, detector_coverage,
    has_recommendation_boost, score_distribution,
)


class EvaluationRunner:
    def __init__(self) -> None:
        self._qu = QueryUnderstandingService()
        self._svc = build_search_catalog_service()

    def run_all(self, dataset: list[TestCase]) -> EvaluationSummary:
        results: list[SingleResult] = []
        detectors_ok: dict[str, int] = {}
        detectors_total: dict[str, int] = {}
        all_scores: list[float] = []
        all_times: list[float] = []
        all_pipeline_times: list[float] = []
        all_precisions_1: list[float] = []
        all_precisions_3: list[float] = []
        all_precisions_5: list[float] = []
        all_recalls_5: list[float] = []
        retrieved_lists: list[list[str]] = []
        expected_lists: list[list[str]] = []
        boosted = 0
        worsened = 0
        improved = 0
        hardest: list[tuple] = []

        for case in dataset:
            t0 = time.perf_counter()
            structured = self._qu.understand(case.query)
            t1 = time.perf_counter()
            query_time = (t1 - t0) * 1000

            response = self._svc.search(structured, max_results=20)
            t2 = time.perf_counter()
            pipeline_time = (t2 - t0) * 1000

            retrieved = []
            scores = []
            explanations = []
            for r in response.results[:10]:
                retrieved.append(r.product.reference)
                scores.append(r.relevance_score)
                all_scores.append(r.relevance_score)
                if r.explanation:
                    explanations.append(r.explanation.summary)
                else:
                    explanations.append("")

            detector = DetectorResult(
                families=structured.detected_product_types,
                categories=structured.detected_categories,
                materials=structured.detected_materials,
                attributes=structured.detected_attributes,
                audience=structured.detected_audience,
                technologies=structured.detected_technologies or [],
                capacity=structured.detected_capacity,
            )

            all_times.append(query_time)
            all_pipeline_times.append(pipeline_time)
            retrieved_lists.append(retrieved)
            expected_lists.append(case.expected_results)

            p1 = precision_at_k(retrieved, case.expected_results, 1)
            p3 = precision_at_k(retrieved, case.expected_results, 3)
            p5 = precision_at_k(retrieved, case.expected_results, 5)
            r5 = recall_at_k(retrieved, case.expected_results, 5)
            all_precisions_1.append(p1)
            all_precisions_3.append(p3)
            all_precisions_5.append(p5)
            all_recalls_5.append(r5)

            # Detector accuracy
            if case.expected_families:
                detectors_total["families"] = detectors_total.get("families", 0) + 1
                acc = detector_accuracy(detector.families, case.expected_families)
                if acc >= 1.0:
                    detectors_ok["families"] = detectors_ok.get("families", 0) + 1
            if case.expected_categories:
                detectors_total["categories"] = detectors_total.get("categories", 0) + 1
                acc = detector_accuracy(detector.categories, case.expected_categories)
                if acc >= 1.0:
                    detectors_ok["categories"] = detectors_ok.get("categories", 0) + 1
            if case.expected_materials:
                detectors_total["materials"] = detectors_total.get("materials", 0) + 1
                acc = detector_accuracy(detector.materials, case.expected_materials)
                if acc >= 1.0:
                    detectors_ok["materials"] = detectors_ok.get("materials", 0) + 1
            if case.expected_attributes:
                detectors_total["attributes"] = detectors_total.get("attributes", 0) + 1
                acc = detector_accuracy(detector.attributes, case.expected_attributes)
                if acc >= 1.0:
                    detectors_ok["attributes"] = detectors_ok.get("attributes", 0) + 1
            if case.expected_audience:
                detectors_total["audience"] = detectors_total.get("audience", 0) + 1
                if detector.audience == case.expected_audience:
                    detectors_ok["audience"] = detectors_ok.get("audience", 0) + 1
            if case.expected_technologies:
                detectors_total["technologies"] = detectors_total.get("technologies", 0) + 1
                acc = detector_accuracy(detector.technologies, case.expected_technologies)
                if acc >= 1.0:
                    detectors_ok["technologies"] = detectors_ok.get("technologies", 0) + 1
            if case.expected_capacity:
                detectors_total["capacity"] = detectors_total.get("capacity", 0) + 1
                if detector.capacity == case.expected_capacity:
                    detectors_ok["capacity"] = detectors_ok.get("capacity", 0) + 1

            if has_recommendation_boost(explanations):
                boosted += 1

            results.append(SingleResult(
                query=case.query,
                detector=detector,
                retrieved=retrieved,
                scores=scores,
                explanations=explanations,
                execution_time_ms=round(query_time, 2),
                pipeline_time_ms=round(pipeline_time, 2),
            ))

        # Aggregate metrics
        n = len(dataset)
        avg_p1 = sum(all_precisions_1) / n if n else 0
        avg_p3 = sum(all_precisions_3) / n if n else 0
        avg_p5 = sum(all_precisions_5) / n if n else 0
        avg_r5 = sum(all_recalls_5) / n if n else 0
        avg_search = sum(all_times) / n if n else 0
        avg_pipeline = sum(all_pipeline_times) / n if n else 0

        mrr_val = mrr(retrieved_lists, expected_lists)
        ndcg_val = sum(
            ndcg(ret, exp, 5) for ret, exp in zip(retrieved_lists, expected_lists)
        ) / n if n else 0

        detector_coverage_dict = {}
        for key in detectors_total:
            detector_coverage_dict[key] = {
                "ok": detectors_ok.get(key, 0),
                "total": detectors_total[key],
                "accuracy": round(detectors_ok.get(key, 0) / detectors_total[key] * 100, 1),
            }

        dist = score_distribution(all_scores)

        return EvaluationSummary(
            total_cases=n,
            precision_at_1=round(avg_p1, 4),
            precision_at_3=round(avg_p3, 4),
            precision_at_5=round(avg_p5, 4),
            recall_at_5=round(avg_r5, 4),
            mrr=round(mrr_val, 4),
            ndcg=round(ndcg_val, 4),
            avg_search_time_ms=round(avg_search, 2),
            avg_pipeline_time_ms=round(avg_pipeline, 2),
            detector_coverage=detector_coverage_dict,
            detector_accuracy={},
            boosted_count=boosted,
            avg_score=round(sum(all_scores) / len(all_scores), 4) if all_scores else 0,
            score_distribution=dist,
        )
