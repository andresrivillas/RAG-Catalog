import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import AnalysisReport


def generate_report(
    analysis: AnalysisReport,
    output_path: Optional[Path] = None,
) -> dict:
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_evaluated": analysis.total_evaluated,
        "gaps": {
            "detector_gaps": [
                {"query": g.query, "detector": g.detector,
                 "expected": g.expected, "confidence": g.confidence}
                for g in analysis.detector_gaps
            ],
            "low_detection_queries": analysis.low_detection_queries,
        },
        "candidates": {
            "synonyms": [
                {"term": s.term, "normalized": s.normalized,
                 "frequency": s.frequency, "examples": s.examples[:2]}
                for s in analysis.synonym_candidates[:30]
            ],
        },
        "recommendations": [
            {
                "category": r.category,
                "description": r.description,
                "impact": r.impact,
                "frequency": r.frequency,
                "confidence": r.confidence,
                "effort": r.effort,
            }
            for r in analysis.recommendations
        ],
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    return report


def print_analysis(analysis: AnalysisReport) -> None:
    print("=" * 60)
    print("KNOWLEDGE GAP ANALYSIS REPORT")
    print("=" * 60)
    print(f"Total evaluated: {analysis.total_evaluated}")
    print()

    if analysis.detector_gaps:
        print("DETECTOR GAPS:")
        for g in analysis.detector_gaps[:5]:
            print(f"  {g.detector:12s}: '{' '.join(g.expected)}' en '{g.query}'")
        print()

    if analysis.synonym_candidates:
        print(f"TOP SYNONYM CANDIDATES ({len(analysis.synonym_candidates)} total):")
        for s in analysis.synonym_candidates[:10]:
            ex = ", ".join(e[:30] for e in s.examples)
            print(f"  '{s.term}' (freq={s.frequency}) ej: {ex[:60]}")
        print()

    if analysis.recommendations:
        print("RECOMMENDATIONS:")
        for i, r in enumerate(analysis.recommendations[:15], 1):
            print(f"  {i:2d}. [{r.impact.upper():6s}] [{r.effort:6s}] {r.description}")
        print()
        print(f"Total recommendations: {len(analysis.recommendations)}")
