import logging
from pathlib import Path
from typing import Optional

from config.settings import settings
from .pipeline import run_quality_pipeline
from .dashboard import build_dashboard, print_dashboard_summary

logger = logging.getLogger("smart_catalog.data_quality")


class CatalogDataQualityService:
    def run(self, output_dir: Optional[Path] = None) -> dict:
        if output_dir is None:
            output_dir = Path("data") / "quality"
        output_dir.mkdir(parents=True, exist_ok=True)

        catalog_path = Path(settings.catalog_path).parent.parent / "enriched" / "enriched_catalog.json"
        knowledge_path = Path(settings.catalog_path).parent.parent / "enriched" / "catalog_knowledge.json"

        if not catalog_path.exists():
            logger.error("Catalogo no encontrado: %s", catalog_path)
            return {"error": "catalogo no encontrado"}

        quality_output = output_dir / "catalog_quality_results.json"
        dashboard_output = output_dir / "catalog_quality_dashboard.json"

        dashboard = run_quality_pipeline(
            catalog_path=catalog_path,
            knowledge_path=knowledge_path,
            output_path=quality_output,
            dashboard_path=dashboard_output,
        )

        print_dashboard_summary(dashboard)
        return dashboard
