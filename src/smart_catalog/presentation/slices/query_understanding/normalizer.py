import logging
import re
import unicodedata

from ....knowledge_store.loader import KnowledgeLoader

logger = logging.getLogger("smart_catalog.query_understanding")

_loader = KnowledgeLoader()
_knowledge = _loader.load()

STOP_WORDS = frozenset(_knowledge.stop_words)
GENERIC_TERMS = frozenset(_knowledge.generic_terms)
SYNONYM_MAP: dict[str, str] = dict(_knowledge.normalizer_synonyms)


class QueryNormalizer:
    def normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^a-z0-9\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def remove_stop_words(self, tokens: list[str]) -> list[str]:
        return [t for t in tokens if t not in STOP_WORDS]

    def remove_digits(self, tokens: list[str]) -> list[str]:
        return [t for t in tokens if not t.isdigit()]

    def apply_synonyms(self, tokens: list[str]) -> list[str]:
        replaced = []
        for token in tokens:
            if token in SYNONYM_MAP:
                normalized = SYNONYM_MAP[token]
                replaced.append(normalized.lower())
                logger.debug("Sinonimo: %s -> %s", token, normalized)
            else:
                replaced.append(token)
        return replaced

    def detect_product_types(self, tokens: list[str]) -> list[str]:
        detected = []
        for token in tokens:
            if token in SYNONYM_MAP:
                ptype = SYNONYM_MAP[token]
                if ptype not in detected:
                    detected.append(ptype)
        return detected
