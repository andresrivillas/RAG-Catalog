import logging

logger = logging.getLogger("smart_catalog.query_understanding")

COLOR_KEYWORDS: dict[str, str] = {
    "negro": "NEGRO", "negra": "NEGRO", "negros": "NEGRO", "negras": "NEGRO",
    "blanco": "BLANCO", "blanca": "BLANCO", "blancos": "BLANCO", "blancas": "BLANCO",
    "azul": "AZUL", "azules": "AZUL",
    "rojo": "ROJO", "roja": "ROJO", "rojos": "ROJO", "rojas": "ROJO",
    "verde": "VERDE", "verdes": "VERDE",
    "gris": "GRIS", "grises": "GRIS",
    "plateado": "PLATEADO", "plateada": "PLATEADO",
    "dorado": "DORADO", "dorada": "DORADO",
    "amarillo": "AMARILLO", "amarilla": "AMARILLO",
    "naranja": "NARANJA",
    "morado": "MORADO", "morada": "MORADO", "violeta": "MORADO",
    "rosa": "ROSA", "rosado": "ROSA", "rosada": "ROSA",
    "cafe": "CAFE", "marron": "CAFE",
    "beige": "BEIGE",
    "transparente": "TRANSPARENTE",
}


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
