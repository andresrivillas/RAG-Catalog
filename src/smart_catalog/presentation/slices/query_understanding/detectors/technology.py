import logging
import re

from .....knowledge_store.loader import KnowledgeLoader

logger = logging.getLogger("smart_catalog.query_understanding")

_loader = KnowledgeLoader()
_knowledge = _loader.load()

TECH_SIGNALS: list[tuple[str, str, str]] = [
    (t["pattern"], t["name"], t["name"].lower()) for t in _knowledge.technologies
]
TECH_KEYWORDS = {t[2] for t in TECH_SIGNALS}


def detect_technologies(text: str) -> list[str]:
    detected: list[str] = []
    text_lower = text.lower()
    for pattern, name, _ in TECH_SIGNALS:
        if re.search(pattern, text_lower):
            if name not in detected:
                detected.append(name)
                logger.debug("Tecnologia detectada: %s", name)
    return detected


def is_known(token: str) -> bool:
    return token in TECH_KEYWORDS
