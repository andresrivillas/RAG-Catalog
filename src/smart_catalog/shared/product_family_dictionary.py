from typing import Optional

PRODUCT_FAMILIES: dict[str, dict] = {
    "USB": {
        "canonical": "USB",
        "product_types": ["USB"],
        "name_terms": ["usb", "pendrive", "flash", "memory stick"],
        "exclude_categories": [],
    },
    "BOTELLA": {
        "canonical": "Botella",
        "product_types": ["BOTELLA"],
        "name_terms": ["botella", "botilito", "botellon"],
        "exclude_categories": [],
    },
    "LAPICERO": {
        "canonical": "Lapicero",
        "product_types": ["LAPICERO", "LAPIZ", "BOLIGRAFO", "PLUMA"],
        "name_terms": ["lapicero", "lapiz", "boligrafo", "esfero", "pluma"],
        "exclude_categories": [],
    },
    "MUG": {
        "canonical": "Mug",
        "product_types": ["MUG", "VASO"],
        "name_terms": ["mug", "taza", "vaso"],
        "exclude_categories": [],
    },
    "BOLSO": {
        "canonical": "Bolso",
        "product_types": ["BOLSO"],
        "name_terms": ["bolso", "bolsa", "mochila", "cartera", "morral", "maletin", "tula", "tote"],
        "exclude_categories": [],
    },
    "TERMO": {
        "canonical": "Termo",
        "product_types": ["TERMO"],
        "name_terms": ["termo", "termico"],
        "exclude_categories": [],
    },
    "CARGADOR": {
        "canonical": "Cargador",
        "product_types": ["CARGADOR"],
        "name_terms": ["cargador", "power bank", "carga"],
        "exclude_categories": [],
    },
    "AGENDA": {
        "canonical": "Agenda",
        "product_types": ["AGENDA", "LIBRETA"],
        "name_terms": ["agenda", "libreta", "cuaderno", "block"],
        "exclude_categories": [],
    },
    "GORRA": {
        "canonical": "Gorra",
        "product_types": ["GORRA"],
        "name_terms": ["gorra", "visera"],
        "exclude_categories": [],
    },
    "LLAVERO": {
        "canonical": "Llavero",
        "product_types": ["LLAVERO"],
        "name_terms": ["llavero", "portallaves"],
        "exclude_categories": [],
    },
    "RELOJ": {
        "canonical": "Reloj",
        "product_types": ["RELOJ"],
        "name_terms": ["reloj"],
        "exclude_categories": [],
    },
    "PULSERA": {
        "canonical": "Pulsera",
        "product_types": ["PULSERA"],
        "name_terms": ["pulsera"],
        "exclude_categories": [],
    },
    "MOUSE": {
        "canonical": "Mouse",
        "product_types": ["MOUSE"],
        "name_terms": ["mouse", "raton"],
        "exclude_categories": [],
    },
    "AUDIFONOS": {
        "canonical": "Audifonos",
        "product_types": ["AUDIFONOS"],
        "name_terms": ["audifonos", "cascos"],
        "exclude_categories": [],
    },
    "CALCULADORA": {
        "canonical": "Calculadora",
        "product_types": ["CALCULADORA"],
        "name_terms": ["calculadora"],
        "exclude_categories": [],
    },
    "PARAGUAS": {
        "canonical": "Paraguas",
        "product_types": ["PARAGUAS"],
        "name_terms": ["paraguas"],
        "exclude_categories": [],
    },
    "NEVERA": {
        "canonical": "Nevera",
        "product_types": ["NEVERA", "LONCHERA", "BOLSO_TERMICO"],
        "name_terms": ["nevera", "cooler", "lonchera", "termico"],
        "exclude_categories": [],
    },
    "TOALLA": {
        "canonical": "Toalla",
        "product_types": ["TOALLA"],
        "name_terms": ["toalla"],
        "exclude_categories": [],
    },
    "ORGANIZADOR": {
        "canonical": "Organizador",
        "product_types": ["ORGANIZADOR"],
        "name_terms": ["organizador", "bandeja"],
        "exclude_categories": [],
    },
    "REGALO": {
        "canonical": "Regalo",
        "product_types": ["REGALO"],
        "name_terms": ["regalo", "obsequio", "detalle"],
        "exclude_categories": [],
    },
    "ROPA": {
        "canonical": "Ropa",
        "product_types": ["ROPA"],
        "name_terms": ["camisa", "camiseta", "polo", "chaqueta", "delantal"],
        "exclude_categories": [],
    },
}


def resolve_family(product_types: list[str]) -> Optional[str]:
    for pt in product_types:
        for key, family in PRODUCT_FAMILIES.items():
            if pt.upper() in [t.upper() for t in family["product_types"]]:
                return family["canonical"]
    return None


def get_family_key(product_types: list[str]) -> Optional[str]:
    for pt in product_types:
        for key in PRODUCT_FAMILIES:
            if pt.upper() in [t.upper() for t in PRODUCT_FAMILIES[key]["product_types"]]:
                return key
    return None


def get_family_expansions(family_key: str) -> list[str]:
    family = PRODUCT_FAMILIES.get(family_key.upper())
    if not family:
        return []
    return family["name_terms"]


def is_product_in_family(product_name: str, product_category: str, family_key: str) -> bool:
    family = PRODUCT_FAMILIES.get(family_key.upper())
    if not family:
        return False
    name_lower = product_name.lower()
    for term in family["name_terms"]:
        if term in name_lower:
            return True
    for ex_cat in family["exclude_categories"]:
        if ex_cat.lower() in product_category.lower():
            return False
    return False
