import logging
from .....knowledge_store.loader import KnowledgeLoader

logger = logging.getLogger("smart_catalog.query_understanding")

_loader = KnowledgeLoader()
_knowledge = _loader.load()
COLOR_KEYWORDS: dict[str, str] = dict(_knowledge.colors)


def detect_colors(tokens: list[str]) -> list[str]:
    detected = []
    for token in tokens:
        if token in COLOR_KEYWORDS:
            color = COLOR_KEYWORDS[token]
            if color not in detected:
                detected.append(color)
                logger.debug("Color detectado: %s (desde: %s)", color, token)
    return detected


def is_known(token: str) -> bool:
    return token in COLOR_KEYWORDS
