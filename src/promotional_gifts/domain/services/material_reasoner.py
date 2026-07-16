"""Razonamiento difuso de materiales.

Permite inferir que materiales distintos textualmente pertenecen a la misma
familia comercial, por ejemplo:

    madera ~ bambu ~ corcho ~ wood ~ wooden ~ rpet bamboo ~ eco wood

No es igualdad textual: se normaliza el texto y se agrupa por familia.
"""

from typing import Dict, List, Set

MATERIAL_FAMILIES: Dict[str, List[str]] = {
    "madera": [
        "madera", "wood", "wooden", "bambu", "bambú", "corcho", "cork",
        "rpet bamboo", "eco wood", "bamboo", "aglomerado", "mdf",
    ],
    "metal": [
        "metal", "acero", "steel", "aluminio", "aluminum", "cobre", "inoxidable",
    ],
    "cuero": [
        "cuero", "leather", "piel", "napa",
    ],
    "plastico": [
        "plastico", "plástico", "pvc", "polipropileno", "poliester", "poliéster",
        "silicona", "acrilico", "acrílico",
    ],
    "vidrio": [
        "vidrio", "cristal", "glass",
    ],
    "textil": [
        "algodon", "algodón", "lona", "neopreno", "felpa", "fieltro", "tela",
    ],
    "papel": [
        "papel", "carton", "cartón", "kraft", "reciclado", "reciclable",
    ],
    "ecologico": [
        "eco", "ecologico", "ecológico", "sostenible", "rpet", "bambu", "bambú",
        "corcho", "cork", "biodegradable", "organico", "orgánico",
    ],
}

_FAMILY_LOOKUP: Dict[str, str] = {}
for _family, _terms in MATERIAL_FAMILIES.items():
    for _term in _terms:
        _FAMILY_LOOKUP[_term] = _family


def normalize_material(text: str) -> str:
    return " ".join((text or "").lower().split())


def material_families(text: str) -> Set[str]:
    """Devuelve el conjunto de familias presentes en el texto de material."""
    normalized = normalize_material(text)
    if not normalized:
        return set()
    found: Set[str] = set()
    for term, family in _FAMILY_LOOKUP.items():
        if term in normalized:
            found.add(family)
    # Tambien detecta fragmentos compuestos como "rpet bamboo".
    for family, terms in MATERIAL_FAMILIES.items():
        for term in terms:
            if len(term) >= 4 and term in normalized:
                found.add(family)
    return found


def materials_match(a: str, b: str) -> bool:
    """Indica si dos descripciones de material comparten familia comercial."""
    fa = material_families(a)
    fb = material_families(b)
    return bool(fa & fb)


def is_eco_material(text: str) -> bool:
    return "ecologico" in material_families(text)
