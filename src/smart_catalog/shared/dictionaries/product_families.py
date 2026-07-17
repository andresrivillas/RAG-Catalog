from typing import Optional

# ──────────────────────────────────────────────
# Única fuente de verdad para familias de producto
# ──────────────────────────────────────────────

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


# ──────────────────────────────────────────────
# Sinónimos: término normalizado → familia canónica
# Usado por: QueryUnderstanding
# ──────────────────────────────────────────────
PRODUCT_SYNONYMS: dict[str, str] = {
    "botilito": "BOTELLA",
    "botilitos": "BOTELLA",
    "botellon": "BOTELLA",
    "botellones": "BOTELLA",
    "botella": "BOTELLA",
    "botellas": "BOTELLA",
    "termo": "TERMO",
    "termos": "TERMO",
    "lapicero": "LAPICERO",
    "lapiceros": "LAPICERO",
    "esfero": "LAPICERO",
    "esferos": "LAPICERO",
    "boligrafo": "BOLIGRAFO",
    "boligrafos": "BOLIGRAFO",
    "pluma": "PLUMA",
    "plumas": "PLUMA",
    "lapiz": "LAPIZ",
    "lapices": "LAPIZ",
    "mug": "MUG",
    "mugs": "MUG",
    "taza": "MUG",
    "tazas": "MUG",
    "vaso": "VASO",
    "vasos": "VASO",
    "bolso": "BOLSO",
    "bolsos": "BOLSO",
    "mochila": "BOLSO",
    "mochilas": "BOLSO",
    "cartera": "BOLSO",
    "carteras": "BOLSO",
    "morral": "BOLSO",
    "morrales": "BOLSO",
    "agenda": "AGENDA",
    "agendas": "AGENDA",
    "libreta": "LIBRETA",
    "libretas": "LIBRETA",
    "cuaderno": "LIBRETA",
    "cuadernos": "LIBRETA",
    "block": "LIBRETA",
    "blocks": "LIBRETA",
    "usb": "USB",
    "memoria": "USB",
    "memorias": "USB",
    "cargador": "CARGADOR",
    "cargadores": "CARGADOR",
    "regalo": "REGALO",
    "regalos": "REGALO",
    "llavero": "LLAVERO",
    "llaveros": "LLAVERO",
    "gorra": "GORRA",
    "gorras": "GORRA",
    "visera": "GORRA",
    "viseras": "GORRA",
    "calculadora": "CALCULADORA",
    "calculadoras": "CALCULADORA",
    "paraguas": "PARAGUAS",
    "nevera": "NEVERA",
    "neveras": "NEVERA",
    "cooler": "NEVERA",
    "coolers": "NEVERA",
    "lonchera": "LONCHERA",
    "loncheras": "LONCHERA",
    "toalla": "TOALLA",
    "toallas": "TOALLA",
    "reloj": "RELOJ",
    "relojes": "RELOJ",
    "gafas": "GAFAS",
    "pulsera": "PULSERA",
    "pulseras": "PULSERA",
    "monedero": "MONEDERO",
    "monederos": "MONEDERO",
    "neceser": "NECESER",
    "neceseres": "NECESER",
    "mouse": "MOUSE",
    "raton": "MOUSE",
    "teclado": "TECLADO",
    "teclados": "TECLADO",
    "audifonos": "AUDIFONOS",
    "cascos": "AUDIFONOS",
    "hub": "HUB",
    "cable": "CABLE",
    "cables": "CABLE",
    "linterna": "LINTERNA",
    "linternas": "LINTERNA",
    "camisa": "ROPA",
    "camisas": "ROPA",
    "camiseta": "ROPA",
    "camisetas": "ROPA",
    "polo": "ROPA",
    "polos": "ROPA",
    "chaqueta": "ROPA",
    "chaquetas": "ROPA",
    "delantal": "ROPA",
    "delantales": "ROPA",
    "bolso_termico": "BOLSO_TERMICO",
    "nevera_portatil": "NEVERA",
    "organizador": "ORGANIZADOR",
    "organizadores": "ORGANIZADOR",
    "maleta": "MALETA",
    "maletas": "MALETA",
    "maletin": "MALETA",
    "maletines": "MALETA",
    "portafolio": "PORTAFOLIO",
    "portafolios": "PORTAFOLIO",
    "billetera": "BILLETERA",
    "billeteras": "BILLETERA",
    "tarjetero": "TARJETERO",
    "tarjeteros": "TARJETERO",
    "portatarjetas": "TARJETERO",
    "portacredencial": "TARJETERO",
}

# ──────────────────────────────────────────────
# Expansiones semánticas: familia → términos de búsqueda
# Usado por: SemanticQueryExpansion
# ──────────────────────────────────────────────
PRODUCT_EXPANSIONS: dict[str, list[str]] = {
    "BOTELLA": [
        "botella", "termo", "botella termica", "botellon",
        "botella metalica", "botella acero", "botella aluminio",
    ],
    "TERMO": [
        "termo", "botella termica", "termico", "termo metalico",
        "botella caliente", "botella frio", "aislante",
    ],
    "LAPICERO": [
        "lapicero", "boligrafo", "esfero", "lapiz", "escritura",
        "boligrafo promocional", "lapiz corporativo",
    ],
    "BOLIGRAFO": [
        "boligrafo", "lapicero", "esfero", "lapiz", "escritura",
    ],
    "LAPIZ": [
        "lapiz", "lapicero", "boligrafo", "grafito", "escritura",
    ],
    "PLUMA": [
        "pluma", "lapicero", "boligrafo", "escritura fina",
    ],
    "MUG": [
        "mug", "taza", "vaso", "ceramica", "mug corporativo",
        "taza promocional", "mug ceramica",
    ],
    "VASO": [
        "vaso", "mug", "taza", "vaso corporativo", "cristaleria",
    ],
    "BOLSO": [
        "bolso", "bolsa", "mochila", "cartera", "morral",
        "bolsa corporativa", "bolsa promocional",
    ],
    "USB": [
        "usb", "memoria usb", "hub usb", "puerto usb",
        "pendrive", "dispositivo usb",
    ],
    "CARGADOR": [
        "cargador", "cargador inalambrico", "cargador movil",
        "cargador usb", "cargador coche", "power bank",
    ],
    "AGENDA": [
        "agenda", "libreta", "cuaderno", "block", "agenda corporativa",
        "agenda promocional",
    ],
    "LIBRETA": [
        "libreta", "cuaderno", "agenda", "block", "libreta corporativa",
    ],
    "REGALO": [
        "regalo empresarial", "regalo corporativo", "obsequio",
        "detalle promocional", "articulo promocional",
    ],
    "LLAVERO": [
        "llavero", "llaveros", "portallaves", "llavero promocional",
    ],
    "GORRA": [
        "gorra", "visera", "gorra corporativa", "gorra promocional",
    ],
    "CALCULADORA": [
        "calculadora", "calculadora corporativa", "calculadora promocional",
    ],
    "PARAGUAS": [
        "paraguas", "paraguas corporativo", "paraguas promocional",
    ],
    "NEVERA": [
        "nevera", "cooler", "nevera portatil", "bolso termico",
        "nevera corporativa",
    ],
    "LONCHERA": [
        "lonchera", "nevera portatil", "bolso termico",
    ],
    "TOALLA": [
        "toalla", "toalla corporativa", "toalla promocional",
    ],
    "RELOJ": [
        "reloj", "reloj corporativo", "reloj promocional",
    ],
    "GAFAS": [
        "gafas", "lentes", "gafas corporativas",
    ],
    "PULSERA": [
        "pulsera", "pulsera corporativa", "pulsera promocional",
    ],
    "MONEDERO": [
        "monedero", "monedero corporativo", "billetera",
    ],
    "NECESER": [
        "neceser", "estuche", "cosmetiquera",
    ],
    "MOUSE": [
        "mouse", "raton", "mouse pad", "accesorio computacion",
    ],
    "TECLADO": [
        "teclado", "teclado corporativo",
    ],
    "AUDIFONOS": [
        "audifonos", "cascos", "audifonos corporativos",
    ],
    "HUB": [
        "hub", "hub usb", "multipuerto",
    ],
    "CABLE": [
        "cable", "cable usb", "cable carga",
    ],
    "LINTERNA": [
        "linterna", "linterna corporativa", "luz led",
    ],
    "ROPA": [
        "camisa", "camiseta", "polo", "chaqueta", "delantal",
        "ropa corporativa",
    ],
    "ORGANIZADOR": [
        "organizador", "organizador escritorio", "bandeja",
    ],
    "MALETA": [
        "maleta", "maletin", "portafolio", "maleta corporativa",
    ],
    "BOLSO_TERMICO": [
        "bolso termico", "nevera portatil", "lonchera",
    ],
    "PORTAFOLIO": [
        "portafolio", "maletin", "carpeta corporativa",
    ],
    "BILLETERA": [
        "billetera", "monedero", "tarjetero",
    ],
    "TARJETERO": [
        "tarjetero", "portatarjetas", "portacredencial",
        "tarjetero corporativo",
    ],
}

# ──────────────────────────────────────────────
# Utilidades
# ──────────────────────────────────────────────

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
