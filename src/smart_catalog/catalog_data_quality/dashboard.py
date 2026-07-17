import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import CatalogQuality, classify_score


def build_dashboard(
    qualities: list[CatalogQuality],
    output_path: Optional[Path] = None,
) -> dict:
    total = len(qualities)
    if total == 0:
        return {"error": "no hay productos"}

    levels = Counter(q.classification_level for q in qualities)
    scores = [q.data_quality_score for q in qualities]
    completeness = [q.completeness_score for q in qualities]
    metadata = [q.metadata_score for q in qualities]
    commercial = [q.commercial_score for q in qualities]
    evidence = [q.evidence_score for q in qualities]
    priorities = [q.improvement_priority for q in qualities]

    has_materials = sum(1 for q in qualities if q.has_materials)
    has_description = sum(1 for q in qualities if q.has_description)
    has_tags = sum(1 for q in qualities if q.has_tags)
    has_colors = sum(1 for q in qualities if q.has_colors)
    has_family = sum(1 for q in qualities if q.has_family)
    has_commercial_strong = sum(1 for q in qualities if q.has_commercial_knowledge_strong)
    generic_cats = sum(1 for q in qualities if q.category_is_generic)

    missing_materials = sum(1 for q in qualities if "materials" in q.missing_fields)
    missing_desc = sum(1 for q in qualities if "description" in q.missing_fields)
    missing_tags = sum(1 for q in qualities if "commercial_tags" in q.missing_fields)
    missing_colors = sum(1 for q in qualities if "colors" in q.missing_fields)

    all_problems: Counter[str] = Counter()
    for q in qualities:
        for p in q.detected_problems:
            all_problems[p.code] += 1

    top_priorities = sorted(qualities, key=lambda q: q.improvement_priority, reverse=True)[:100]

    dashboard = {
        "generated_at": datetime.now().isoformat(),
        "total_products": total,
        "summary": {
            "avg_quality_score": round(sum(scores) / total, 4),
            "avg_completeness": round(sum(completeness) / total, 4),
            "avg_metadata": round(sum(metadata) / total, 4),
            "avg_commercial": round(sum(commercial) / total, 4),
            "avg_evidence": round(sum(evidence) / total, 4),
            "avg_priority": round(sum(priorities) / total, 4),
            "score_min": round(min(scores), 4),
            "score_max": round(max(scores), 4),
            "score_median": round(sorted(scores)[total // 2], 4),
        },
        "distribution": {
            "excelente": levels.get("excelente", 0),
            "bueno": levels.get("bueno", 0),
            "aceptable": levels.get("aceptable", 0),
            "pobre": levels.get("pobre", 0),
            "critico": levels.get("critico", 0),
        },
        "coverage": {
            "con_materiales": f"{has_materials}/{total} ({has_materials/total*100:.0f}%)",
            "con_descripcion": f"{has_description}/{total} ({has_description/total*100:.0f}%)",
            "con_tags": f"{has_tags}/{total} ({has_tags/total*100:.0f}%)",
            "con_colores": f"{has_colors}/{total} ({has_colors/total*100:.0f}%)",
            "con_familia": f"{has_family}/{total} ({has_family/total*100:.0f}%)",
            "con_commercial_strong": f"{has_commercial_strong}/{total} ({has_commercial_strong/total*100:.0f}%)",
            "categoria_generica": f"{generic_cats}/{total} ({generic_cats/total*100:.0f}%)",
        },
        "missing_fields": {
            "sin_materiales": missing_materials,
            "sin_descripcion": missing_desc,
            "sin_tags": missing_tags,
            "sin_colores": missing_colors,
        },
        "top_problems": [(code, count) for code, count in all_problems.most_common(15)],
        "top_100_priorities": [
            {
                "reference": q.product_reference,
                "name": q.product_name,
                "score": q.data_quality_score,
                "level": q.classification_level,
                "priority": q.improvement_priority,
                "missing": q.missing_fields[:5],
                "recommendations": q.recommendations[:3],
            }
            for q in top_priorities
        ],
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dashboard, f, indent=2, ensure_ascii=False)

    return dashboard


def print_dashboard_summary(dashboard: dict) -> None:
    s = dashboard.get("summary", {})
    dist = dashboard.get("distribution", {})
    cov = dashboard.get("coverage", {})

    print("=" * 60)
    print("DASHBOARD DE CALIDAD DEL CATALOGO")
    print("=" * 60)
    print(f"Total productos: {dashboard['total_products']}")
    print(f"Score promedio:  {s.get('avg_quality_score', 0):.4f}")
    print(f"Completitud:     {s.get('avg_completeness', 0):.4f}")
    print(f"Metadata:        {s.get('avg_metadata', 0):.4f}")
    print(f"Comercial:       {s.get('avg_commercial', 0):.4f}")
    print(f"Evidencia:       {s.get('avg_evidence', 0):.4f}")
    print()
    print("DISTRIBUCION:")
    for level in ("excelente", "bueno", "aceptable", "pobre", "critico"):
        count = dist.get(level, 0)
        pct = count / dashboard["total_products"] * 100 if dashboard["total_products"] else 0
        print(f"  {level:12s}: {count:5d} ({pct:5.1f}%)")
    print()
    print("COBERTURA:")
    for k, v in cov.items():
        print(f"  {k:25s}: {v}")
    print()
    print("TOP 10 PROBLEMAS:")
    for code, count in dashboard.get("top_problems", [])[:10]:
        print(f"  {code:40s}: {count}")
    print()
    print("TOP 5 PRIORIDADES:")
    for item in dashboard.get("top_100_priorities", [])[:5]:
        print(f"  {item['reference']:20s} {item['name'][:35]:35s} score={item['score']:.2f} prioridad={item['priority']:.2f}")
        for r in item.get("recommendations", []):
            print(f"    -> {r}")
