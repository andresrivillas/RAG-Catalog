import logging
from .....knowledge_store.loader import KnowledgeLoader

logger = logging.getLogger("smart_catalog.query_understanding")

_loader = KnowledgeLoader()
_knowledge = _loader.load()
ATTRIBUTE_KEYWORDS: dict[str, str] = dict(_knowledge.attributes)


def detect_attributes(tokens: list[str]) -> list[str]:
    detected = []
    for token in tokens:
        if token in ATTRIBUTE_KEYWORDS:
            attr = ATTRIBUTE_KEYWORDS[token]
            if attr not in detected:
                detected.append(attr)
                logger.debug("Atributo detectado: %s (desde: %s)", attr, token)
    return detected


def is_known(token: str) -> bool:
    return token in ATTRIBUTE_KEYWORDS
