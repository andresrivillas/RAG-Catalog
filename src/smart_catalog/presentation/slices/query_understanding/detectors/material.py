import logging

logger = logging.getLogger("smart_catalog.query_understanding")

MATERIAL_KEYWORDS: dict[str, str] = {
    "metalico": "METAL", "metalica": "METAL", "metal": "METAL",
    "metalicos": "METAL", "metalicas": "METAL",
    "acero": "METAL", "inoxidable": "METAL", "aluminio": "METAL",
    "rpet": "RPET",
    "bambu": "BAMBU",
    "corcho": "CORCHO",
    "algodon": "ALGODON",
    "madera": "MADERA",
    "plastico": "PLASTICO", "plastica": "PLASTICO",
    "plasticos": "PLASTICO", "plasticas": "PLASTICO",
    "vidrio": "VIDRIO", "cristal": "VIDRIO",
    "ceramica": "CERAMICA", "porcelana": "CERAMICA",
    "cuero": "CUERO", "piel": "CUERO",
    "sintetico": "SINTETICO",
    "poliester": "POLIESTER",
    "polipropileno": "POLIPROPILENO",
    "neopreno": "NEOPRENO",
    "silicone": "SILICONA", "silicona": "SILICONA",
    "caucho": "CAUCHO", "goma": "CAUCHO",
    "tela": "TELA", "textil": "TELA",
    "yute": "YUTE", "yuta": "YUTE",
    "lona": "LONA",
    "lienzo": "LIENZO",
}


def detect_materials(tokens: list[str]) -> list[str]:
    detected = []
    for token in tokens:
        if token in MATERIAL_KEYWORDS:
            material = MATERIAL_KEYWORDS[token]
            if material not in detected:
                detected.append(material)
                logger.debug("Material detectado: %s (desde: %s)", material, token)
    return detected


def is_known(token: str) -> bool:
    return token in MATERIAL_KEYWORDS
