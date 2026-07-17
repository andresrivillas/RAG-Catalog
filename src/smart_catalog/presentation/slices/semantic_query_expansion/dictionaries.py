from ....shared.dictionaries.product_families import PRODUCT_EXPANSIONS
from ....shared.dictionaries.categories import CATEGORY_EXPANSIONS
from ....knowledge_store.loader import KnowledgeLoader

_loader = KnowledgeLoader()
_knowledge = _loader.load()

MATERIAL_EXPANSIONS: dict[str, list[str]] = {}
for term, canonical in _knowledge.materials.items():
    if canonical not in MATERIAL_EXPANSIONS:
        MATERIAL_EXPANSIONS[canonical] = []
    if term not in MATERIAL_EXPANSIONS[canonical]:
        MATERIAL_EXPANSIONS[canonical].append(term)

QUALITY_EXPANSIONS: list[str] = list(_knowledge.quality_keywords)
PRICE_LOW_EXPANSIONS: list[str] = list(_knowledge.low_price_keywords)
PRICE_HIGH_EXPANSIONS: list[str] = list(_knowledge.high_price_keywords)
ECO_EXPANSIONS: list[str] = list(_knowledge.eco_keywords)

ATTRIBUTE_EXPANSIONS: dict[str, list[str]] = {}
for term, canonical in _knowledge.attributes.items():
    if canonical not in ATTRIBUTE_EXPANSIONS:
        ATTRIBUTE_EXPANSIONS[canonical] = []
    if term not in ATTRIBUTE_EXPANSIONS[canonical]:
        ATTRIBUTE_EXPANSIONS[canonical].append(term)

COLOR_EXPANSIONS: dict[str, list[str]] = {}
for term, canonical in _knowledge.colors.items():
    if canonical not in COLOR_EXPANSIONS:
        COLOR_EXPANSIONS[canonical] = []
    if term not in COLOR_EXPANSIONS[canonical]:
        COLOR_EXPANSIONS[canonical].append(term)
