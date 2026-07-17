import logging

from .....shared.dictionaries.categories import CATEGORY_KEYWORDS

logger = logging.getLogger("smart_catalog.query_understanding")


def detect_categories(tokens: list[str]) -> list[str]:
    detected = []
    for token in tokens:
        if token in CATEGORY_KEYWORDS:
            cat = CATEGORY_KEYWORDS[token]
            if cat not in detected:
                detected.append(cat)
                logger.debug("Categoria detectada: %s (desde: %s)", cat, token)
    return detected


def is_known(token: str) -> bool:
    return token in CATEGORY_KEYWORDS
