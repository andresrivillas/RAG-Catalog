import logging
from typing import Optional

from .....knowledge_store.loader import KnowledgeLoader

logger = logging.getLogger("smart_catalog.query_understanding")

_loader = KnowledgeLoader()
_knowledge = _loader.load()

LOW_PRICE_KEYWORDS = frozenset(_knowledge.low_price_keywords)
HIGH_PRICE_KEYWORDS = frozenset(_knowledge.high_price_keywords)
QUALITY_KEYWORDS = frozenset(_knowledge.quality_keywords)
ECO_KEYWORDS = frozenset(_knowledge.eco_keywords)
ALL_INTENT_KEYWORDS = LOW_PRICE_KEYWORDS | HIGH_PRICE_KEYWORDS | ECO_KEYWORDS | QUALITY_KEYWORDS


def detect_price_intent(tokens: list[str]) -> Optional[str]:
    for token in tokens:
        if token in LOW_PRICE_KEYWORDS:
            logger.debug("Intencion de precio baja: %s", token)
            return "LOW_PRICE"
    for token in tokens:
        if token in HIGH_PRICE_KEYWORDS:
            logger.debug("Intencion de precio alta: %s", token)
            return "HIGH_PRICE"
    return None


def detect_quality_intent(tokens: list[str]) -> Optional[str]:
    for token in tokens:
        if token in QUALITY_KEYWORDS:
            logger.debug("Intencion de calidad: %s", token)
            return "HIGH_QUALITY"
    return None


def detect_eco_intent(tokens: list[str]) -> bool:
    for token in tokens:
        if token in ECO_KEYWORDS:
            logger.debug("Intencion eco detectada: %s", token)
            return True
    return False


def is_known(token: str) -> bool:
    return token in ALL_INTENT_KEYWORDS
