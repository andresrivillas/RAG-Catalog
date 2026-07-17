import logging
from .....knowledge_store.loader import KnowledgeLoader

logger = logging.getLogger("smart_catalog.query_understanding")

_loader = KnowledgeLoader()
_knowledge = _loader.load()
MATERIAL_KEYWORDS: dict[str, str] = dict(_knowledge.materials)


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
