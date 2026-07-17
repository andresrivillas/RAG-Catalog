import json
import logging
from pathlib import Path
from typing import Optional

from config.settings import settings

from .store import CatalogKnowledgeStore
from .enricher import enrich_catalog, enrich_single_product

logger = logging.getLogger("smart_catalog.catalog_knowledge_enrichment")


class CatalogKnowledgeEnrichmentService:
    def __init__(self, store: Optional[CatalogKnowledgeStore] = None) -> None:
        self._store = store or CatalogKnowledgeStore(
            path=Path(settings.catalog_path).parent.parent / "enriched" / "catalog_knowledge.json"
        )

    def ensure_enriched(self) -> bool:
        self._store.load()
        if not self._store.needs_enrichment():
            logger.info("Catálogo ya enriquecido: %d productos", self._store.count())
            return True
        catalog_path = Path(settings.catalog_path).parent.parent / "enriched" / "enriched_catalog.json"
        if not catalog_path.exists():
            logger.warning("No se encontró catálogo enriquecido en %s", catalog_path)
            return False
        with open(catalog_path, "r", encoding="utf-8") as f:
            products = json.load(f)
        count = enrich_catalog(products, self._store)
        logger.info("Enriquecimiento completado: %d productos", count)
        return True

    def get_knowledge(self, reference: str):
        self._store.load()
        return self._store.get(reference)

    def get_store(self) -> CatalogKnowledgeStore:
        return self._store
