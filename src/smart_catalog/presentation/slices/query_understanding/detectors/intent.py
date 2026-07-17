import logging
from typing import Optional

logger = logging.getLogger("smart_catalog.query_understanding")

LOW_PRICE_KEYWORDS = frozenset({
    "barato", "baratos", "barata", "baratas",
    "economico", "economicamente", "economica", "economicos", "economicas",
    "bajo_costo", "bajo_coste",
    "accesible", "accesibles",
    "oferta", "ofertas",
    "descuento", "descuentos",
    "promocion", "promociones",
    "gratis", "gratuito", "gratuita",
    "regalado", "regalada",
})

HIGH_PRICE_KEYWORDS = frozenset({
    "caro", "caros", "cara", "caras",
    "premium",
    "lujoso", "lujosa", "lujosos", "lujosas",
    "alta_gama",
    "exclusivo", "exclusiva", "exclusivos", "exclusivas",
    "lujo",
    "delujo", "delujosa",
    "ostentoso", "ostentosa",
    "elegante", "elegantes",
})

QUALITY_KEYWORDS = frozenset({
    "premium",
    "ejecutivo", "ejecutiva",
    "elegante", "elegantes",
    "lujo", "lujoso", "lujosa",
    "alta_calidad",
    "corporativo", "corporativa",
    "profesional",
    "fino", "fina",
    "superior",
    "calidad",
    "excelente",
    "prestigio",
})

ECO_KEYWORDS = frozenset({
    "eco", "ecologico", "ecologica", "ecologicos", "ecologicas",
    "ecofriendly", "eco_friendly",
    "sostenible", "sostenibles",
    "reciclado", "reciclada", "reciclados", "recicladas",
    "reciclable", "reciclables",
    "verde", "verdes",
    "natural", "naturales",
    "organico", "organica", "organicos", "organicas",
    "biodegradable", "biodegradables",
    "rpet",
    "ambiente", "ambiental",
    "ecoconsciente",
    "sustentable", "sustentables",
})

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
