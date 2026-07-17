import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import EvaluationSummary


def generate_report(
    summary: EvaluationSummary,
    output_path: Optional[Path] = None,
) -> dict:
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_cases": summary.total_cases,
        "metrics": {
            "precision_at_1": summary.precision_at_1,
            "precision_at_3": summary.precision_at_3,
            "precision_at_5": summary.precision_at_5,
            "recall_at_5": summary.recall_at_5,
            "mrr": summary.mrr,
            "ndcg": summary.ndcg,
            "avg_search_time_ms": summary.avg_search_time_ms,
            "avg_pipeline_time_ms": summary.avg_pipeline_time_ms,
        },
        "detectors": summary.detector_coverage,
        "commercial_boost": {
            "boosted_queries": summary.boosted_count,
            "boosted_pct": round(summary.boosted_count / max(summary.total_cases, 1) * 100, 1),
            "improved_by_boost": summary.improved_count,
            "worsened_by_boost": summary.worsened_count,
        },
        "scores": {
            "avg_score": summary.avg_score,
            "distribution": summary.score_distribution,
        },
        "performance": {
            "avg_search_time_ms": summary.avg_search_time_ms,
            "avg_pipeline_time_ms": summary.avg_pipeline_time_ms,
        },
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    return report


def print_summary(summary: EvaluationSummary) -> None:
    print("=" * 60)
    print("EVALUATION REPORT - SMART CATALOG SEARCH")
    print("=" * 60)
    print(f"Total test cases: {summary.total_cases}")
    print()
    print("METRICS:")
    print(f"  Precision@1: {summary.precision_at_1:.4f}")
    print(f"  Precision@3: {summary.precision_at_3:.4f}")
    print(f"  Precision@5: {summary.precision_at_5:.4f}")
    print(f"  Recall@5:    {summary.recall_at_5:.4f}")
    print(f"  MRR:         {summary.mrr:.4f}")
    print(f"  NDCG:        {summary.ndcg:.4f}")
    print()
    print("DETECTOR ACCURACY:")
    for name, info in summary.detector_coverage.items():
        print(f"  {name:15s}: {info['ok']}/{info['total']} ({info['accuracy']}%)")
    print()
    print(f"COMMERCIAL BOOST: {summary.boosted_count}/{summary.total_cases} ({round(summary.boosted_count/max(summary.total_cases,1)*100,1)}%)")
    print(f"  Improved by boost:  {summary.improved_count}")
    print(f"  Worsened by boost:  {summary.worsened_count}")
    print()
    print("SCORES:")
    print(f"  Average: {summary.avg_score:.4f}")
    for bucket, count in sorted(summary.score_distribution.items()):
        if count:
            bar = "#" * min(count, 50)
            print(f"  {bucket:8s}: {count:4d} {bar}")
    print()
    print("PERFORMANCE:")
    print(f"  Avg search time:    {summary.avg_search_time_ms:.1f}ms")
    print(f"  Avg pipeline time:  {summary.avg_pipeline_time_ms:.1f}ms")
