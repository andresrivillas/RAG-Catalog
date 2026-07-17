import logging
from pathlib import Path
from typing import Optional

import yaml

from .models import KnowledgeSet
from .cache import KnowledgeCache
from .validator import KnowledgeValidator

logger = logging.getLogger("smart_catalog.knowledge_loader")

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "config" / "knowledge"


class KnowledgeLoader:
    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self._base = base_dir or KNOWLEDGE_DIR
        self._cache = KnowledgeCache(ttl_seconds=300)
        self._validator = KnowledgeValidator()

    def load(self) -> KnowledgeSet:
        cached = self._cache.get()
        if cached is not None:
            return cached

        knowledge = KnowledgeSet()
        self._load_product_families(knowledge)
        self._load_categories(knowledge)
        self._load_materials(knowledge)
        self._load_colors(knowledge)
        self._load_attributes(knowledge)
        self._load_technologies(knowledge)
        self._load_audiences(knowledge)
        self._load_intents(knowledge)
        self._load_normalizer(knowledge)

        valid = self._validator.validate(knowledge)
        if not valid:
            logger.warning("Knowledge validation found %d errors", len(self._validator.errors))

        self._cache.set(knowledge)
        return knowledge

    def _yaml(self, name: str) -> dict:
        path = self._base / name
        if not path.exists():
            logger.warning("Knowledge file not found: %s", path)
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _load_product_families(self, k: KnowledgeSet) -> None:
        data = self._yaml("product_families.yaml")
        for name, info in data.get("details", {}).items():
            k.product_families[name] = info
        data2 = self._yaml("product_synonyms.yaml")
        for term, family in data2.get("synonyms", {}).items():
            k.product_synonyms[term] = family
            k.normalizer_synonyms[term] = family
        data3 = self._yaml("product_expansions.yaml")
        for fam, terms in data3.get("expansions", {}).items():
            k.product_expansions[fam] = terms

    def _load_categories(self, k: KnowledgeSet) -> None:
        data = self._yaml("categories.yaml")
        for term, cat in data.get("keywords", {}).items():
            k.categories[term] = cat
        data2 = self._yaml("category_expansions.yaml")
        for cat, terms in data2.get("expansions", {}).items():
            k.category_expansions[cat] = terms

    def _load_materials(self, k: KnowledgeSet) -> None:
        data = self._yaml("materials.yaml")
        for term, mat in data.get("materials", {}).items():
            k.materials[term] = mat

    def _load_colors(self, k: KnowledgeSet) -> None:
        data = self._yaml("colors.yaml")
        for term, col in data.get("colors", {}).items():
            k.colors[term] = col

    def _load_attributes(self, k: KnowledgeSet) -> None:
        data = self._yaml("attributes.yaml")
        for term, attr in data.get("attributes", {}).items():
            k.attributes[term] = attr

    def _load_technologies(self, k: KnowledgeSet) -> None:
        data = self._yaml("technologies.yaml")
        k.technologies = data.get("technologies", [])

    def _load_audiences(self, k: KnowledgeSet) -> None:
        data = self._yaml("audiences.yaml")
        for item in data.get("patterns", []):
            k.audience_patterns.append((item["pattern"], item["audience"]))

    def _load_intents(self, k: KnowledgeSet) -> None:
        data = self._yaml("intents.yaml")
        k.low_price_keywords = data.get("low_price", [])
        k.high_price_keywords = data.get("high_price", [])
        k.quality_keywords = data.get("quality", [])
        k.eco_keywords = data.get("eco", [])

    def _load_normalizer(self, k: KnowledgeSet) -> None:
        data = self._yaml("normalizer.yaml")
        k.stop_words = data.get("stop_words", [])
        k.generic_terms = data.get("generic_terms", [])
        for term, family in data.get("synonyms", {}).items():
            k.normalizer_synonyms[term] = family
