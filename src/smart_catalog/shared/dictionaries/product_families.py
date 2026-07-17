from typing import Optional

from ...knowledge_store.loader import KnowledgeLoader

_loader = KnowledgeLoader()
_knowledge = _loader.load()

PRODUCT_FAMILIES: dict[str, dict] = {k: {"canonical": k, **v} for k, v in _knowledge.product_families.items()}
PRODUCT_SYNONYMS: dict[str, str] = dict(_knowledge.product_synonyms)
PRODUCT_EXPANSIONS: dict[str, list[str]] = dict(_knowledge.product_expansions)


def resolve_family(product_types: list[str]) -> Optional[str]:
    for pt in product_types:
        for key, family in PRODUCT_FAMILIES.items():
            if pt.upper() in [t.upper() for t in family.get("product_types", [])]:
                return family.get("canonical", key)
    return None


def get_family_key(product_types: list[str]) -> Optional[str]:
    for pt in product_types:
        for key in PRODUCT_FAMILIES:
            if pt.upper() in [t.upper() for t in PRODUCT_FAMILIES[key].get("product_types", [])]:
                return key
    return None


def get_family_expansions(family_key: str) -> list[str]:
    family = PRODUCT_FAMILIES.get(family_key.upper())
    if not family:
        return []
    return family.get("name_terms", [])


def is_product_in_family(product_name: str, product_category: str, family_key: str) -> bool:
    family = PRODUCT_FAMILIES.get(family_key.upper())
    if not family:
        return False
    name_lower = product_name.lower()
    for term in family.get("name_terms", []):
        if term in name_lower:
            return True
    for ex_cat in family.get("exclude_categories", []):
        if ex_cat.lower() in product_category.lower():
            return False
    return False
