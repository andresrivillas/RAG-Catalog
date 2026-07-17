import json
import logging
from pathlib import Path
from typing import Optional

from .models import CatalogKnowledge

logger = logging.getLogger("smart_catalog.catalog_knowledge_store")


class CatalogKnowledgeStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: dict[str, dict] = {}
        self._loaded = False

    def load(self) -> None:
        if self._path.exists():
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                logger.info("Conocimiento cargado: %d productos desde %s", len(self._data), self._path)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning("Error cargando conocimiento: %s", e)
                self._data = {}
        else:
            logger.info("No existe archivo de conocimiento en %s", self._path)
            self._data = {}
        self._loaded = True

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
        logger.info("Conocimiento guardado: %d productos en %s", len(self._data), self._path)

    def get(self, reference: str) -> Optional[CatalogKnowledge]:
        raw = self._data.get(reference)
        if raw is None:
            return None
        return CatalogKnowledge.from_dict(raw)

    def set(self, reference: str, knowledge: CatalogKnowledge) -> None:
        self._data[reference] = knowledge.to_dict()

    def has(self, reference: str) -> bool:
        return reference in self._data

    def count(self) -> int:
        return len(self._data)

    def needs_enrichment(self) -> bool:
        return not self._loaded or len(self._data) == 0
