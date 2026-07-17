import logging

logger = logging.getLogger("smart_catalog.query_understanding")

ATTRIBUTE_KEYWORDS: dict[str, str] = {
    "personalizable": "PERSONALIZABLE", "personalizado": "PERSONALIZABLE",
    "personalizados": "PERSONALIZABLE", "personalizada": "PERSONALIZABLE",
    "personalizadas": "PERSONALIZABLE",
    "estampado": "ESTAMPADO", "grabado": "GRABADO", "bordado": "BORDADO",
    "ligero": "LIGERO", "ligera": "LIGERO", "liviano": "LIGERO", "liviana": "LIGERO",
    "compacto": "COMPACTO", "compacta": "COMPACTO",
    "portatil": "PORTATIL", "plegable": "PLEGABLE",
    "reutilizable": "REUTILIZABLE",
    "resistente": "RESISTENTE", "impermeable": "IMPERMEABLE",
    "termico": "TERMICO", "termica": "TERMICO", "aislante": "AISLANTE",
}


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
