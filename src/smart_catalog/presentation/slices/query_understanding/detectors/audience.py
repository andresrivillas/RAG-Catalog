import logging
import re
from typing import Optional

from .....knowledge_store.loader import KnowledgeLoader

logger = logging.getLogger("smart_catalog.query_understanding")

_loader = KnowledgeLoader()
_knowledge = _loader.load()
AUDIENCE_PATTERNS: list[tuple[str, str]] = list(_knowledge.audience_patterns)


def detect_audience(text: str) -> Optional[str]:
    for pattern, audience in AUDIENCE_PATTERNS:
        if re.search(pattern, text):
            logger.debug("Audiencia detectada: %s", audience)
            return audience
    return None


def matched_terms(text: str) -> list[str]:
    terms = []
    for pattern, _ in AUDIENCE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            for mt in match.group(0).split():
                terms.append(mt)
    return terms
