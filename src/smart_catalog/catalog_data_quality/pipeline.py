import json
import logging
import time
from pathlib import Path
from typing import Optional

from .models import CatalogQuality, DetectedProblem
from .scorers import assess_product
from .validators import detect_duplicates, validate_product
from .recommendations import generate_recommendations
from .dashboard import build_dashboard, print_dashboard_summary

logger = logging.getLogger("smart_catalog.data_quality")


def run_quality_pipeline(
    catalog_path: Path,
    knowledge_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    dashboard_path: Optional[Path] = None,
) -> dict:
    start = time.perf_counter()

    with open(catalog_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    knowledge_map: dict[str, dict] = {}
    if knowledge_path and knowledge_path.exists():
        with open(knowledge_path, "r", encoding="utf-8") as f:
            knowledge_map = json.load(f)

    logger.info("Evaluando %d productos...", len(products))
    qualities: list[CatalogQuality] = []
    duplicates = detect_duplicates(products)

    for product in products:
        ref = product.get("reference", "")
        name = product.get("name", "")

        ck_raw = knowledge_map.get(ref) if knowledge_map else None
        enrichment_confidence = None
        has_family = False
        has_commercial_strong = False

        if ck_raw:
            family = ck_raw.get("product_family", {})
            if isinstance(family, dict):
                has_family = bool(family.get("value"))
            elif isinstance(family, str):
                has_family = bool(family)
            overall = ck_raw.get("overall_confidence", 0)
            enrichment_confidence = overall if isinstance(overall, (int, float)) else None
            commercial_tags = ck_raw.get("commercial_tags", [])
            has_commercial_strong = len(commercial_tags) > 2

        quality = assess_product(
            product,
            enrichment_confidence=enrichment_confidence,
            has_family=has_family,
            has_commercial_strong=has_commercial_strong,
        )

        problems = validate_product(product)
        quality.detected_problems = problems

        if ref in duplicates:
            dup_refs = [r for r in duplicates[ref] if r != ref]
            if dup_refs:
                problems.append(DetectedProblem(
                    code="potential_duplicate",
                    severity="medium",
                    field="name",
                    description=f"Posible duplicado con: {', '.join(dup_refs[:3])}",
                    suggestion="Verificar si es duplicado real",
                ))

        recommendations = generate_recommendations(quality, product, enrichment_confidence)
        quality.recommendations = recommendations

        qualities.append(quality)

    elapsed = time.perf_counter() - start
    logger.info("Evaluacion completada en %.2fs", elapsed)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([q.to_dict() for q in qualities], f, indent=2, ensure_ascii=False)
        logger.info("Resultados guardados en %s", output_path)

    dashboard = build_dashboard(qualities, output_path=dashboard_path)
    dashboard["products_evaluated"] = len(qualities)
    dashboard["elapsed_seconds"] = round(elapsed, 2)
    dashboard["duplicates_found"] = len(duplicates)

    return dashboard
