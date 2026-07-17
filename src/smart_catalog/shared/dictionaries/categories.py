from ...knowledge_store.loader import KnowledgeLoader

_loader = KnowledgeLoader()
_knowledge = _loader.load()

CANONICAL_CATEGORIES: set[str] = set(_knowledge.categories.values())
CATEGORY_KEYWORDS: dict[str, str] = dict(_knowledge.categories)
CATEGORY_EXPANSIONS: dict[str, list[str]] = dict(_knowledge.category_expansions)
