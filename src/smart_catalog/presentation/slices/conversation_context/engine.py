import logging
import re
import unicodedata
from typing import Optional


def _normalize_word(word: str) -> str:
    word = word.lower().strip()
    word = unicodedata.normalize("NFKD", word)
    word = word.encode("ascii", "ignore").decode("ascii")
    return word

logger = logging.getLogger("smart_catalog.context")

RELATIVE_INDICATORS: frozenset = frozenset({
    "solo", "solamente", "unicamente", "nada mas", "nada más",
    "ahora", "mejor", "mejores", "peor", "peores",
    "tambien", "ademas", "adicionar", "agrega", "agregar", "añadir",
    "quita", "quitar", "elimina", "eliminar", "saca", "sacar",
    "sin", "menos",
    "cambia", "cambiar", "reemplaza", "reemplazar",
    "filtra", "filtrar", "refina", "refinar",
    "mas", "menos",
})

COMPARATIVE_PATTERNS: list[re.Pattern] = [
    re.compile(r"\bmas\s+(baratos?|caros?|economicos?|premium|caros?|grandes?|pequenos?|ligeros?)\b"),
    re.compile(r"\b(menos|mas)\s+de\s+\d"),
    re.compile(r"\bentre\s+\d"),
    re.compile(r"\btop\s+\d+"),
    re.compile(r"\blos\s+mejores\b"),
    re.compile(r"\blos\s+mas\s+\w+"),
]

COMMAND_REMOVE_PATTERNS: list[re.Pattern] = [
    re.compile(r"^(quita|quitar|elimina|eliminar|saca|sacar|sin)\s+"),
]


class ConversationContextEngine:

    def is_relative(self, query: str) -> bool:
        lower = query.lower().strip()

        for indicator in RELATIVE_INDICATORS:
            if lower.startswith(indicator) or f" {indicator} " in f" {lower} ":
                return True

        for pattern in COMPARATIVE_PATTERNS:
            if pattern.search(lower):
                return True

        for pattern in COMMAND_REMOVE_PATTERNS:
            if pattern.search(lower):
                return True

        return False

    def merge_query(self, previous: str, current: str) -> str:
        lower = current.lower().strip()
        prev_lower = previous.lower().strip()

        for pattern in COMMAND_REMOVE_PATTERNS:
            match = pattern.match(lower)
            if match:
                term_to_remove = lower[match.end():].strip()
                words_to_remove = term_to_remove.split()
                prev_words = previous.split()
                filtered = [
                    w for w in prev_words
                    if not any(
                        _normalize_word(rw) in _normalize_word(w)
                        or _normalize_word(w) in _normalize_word(rw)
                        for rw in words_to_remove
                    )
                ]
                result = " ".join(filtered)
                logger.debug(
                    "Eliminacion: '%s' de '%s' -> '%s'",
                    term_to_remove, previous, result,
                )
                return result.strip() or previous

        processed = re.sub(
            r"\b(solo|solamente|unicamente|ahora|tambien|ademas|adicionar|agrega|agregar|refina|refinar|mejor|peor)\b",
            "", lower, flags=re.IGNORECASE,
        ).strip()

        merged = f"{previous} {processed}".strip()
        merged = re.sub(r"\s+", " ", merged)

        logger.debug(
            "Fusion: anterior='%s' + nuevo='%s' -> '%s'",
            previous, current, merged,
        )

        return merged

    def resolve_query(
        self,
        new_query: str,
        previous_query: Optional[str],
    ) -> str:
        if not previous_query:
            logger.debug("Nueva consulta independiente: '%s'", new_query)
            return new_query

        if self.is_relative(new_query):
            resolved = self.merge_query(previous_query, new_query)
            logger.debug(
                "Consulta relativa: '%s' + '%s' -> '%s'",
                previous_query, new_query, resolved,
            )
            return resolved

        logger.debug("Consulta independiente: '%s'", new_query)
        return new_query
