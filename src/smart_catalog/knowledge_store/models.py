from typing import Optional


class KnowledgeSet:
    def __init__(self) -> None:
        self.product_families: dict[str, dict] = {}
        self.product_synonyms: dict[str, str] = {}
        self.product_expansions: dict[str, list[str]] = {}
        self.categories: dict[str, str] = {}
        self.category_expansions: dict[str, list[str]] = {}
        self.materials: dict[str, str] = {}
        self.colors: dict[str, str] = {}
        self.attributes: dict[str, str] = {}
        self.technologies: list[dict] = []
        self.audience_patterns: list[tuple[str, str]] = []
        self.low_price_keywords: list[str] = []
        self.high_price_keywords: list[str] = []
        self.quality_keywords: list[str] = []
        self.eco_keywords: list[str] = []
        self.stop_words: list[str] = []
        self.generic_terms: list[str] = []
        self.normalizer_synonyms: dict[str, str] = {}

    def is_loaded(self) -> bool:
        return len(self.product_families) > 0 or len(self.product_synonyms) > 0
