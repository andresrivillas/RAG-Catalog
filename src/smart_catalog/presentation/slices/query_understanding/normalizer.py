import logging
import re
import unicodedata

logger = logging.getLogger("smart_catalog.query_understanding")

STOP_WORDS = frozenset({
    "de", "la", "los", "las", "del", "para", "con", "por", "en", "un",
    "una", "el", "lo", "y", "e", "o", "a", "al", "que", "es", "se",
    "su", "le", "no", "me", "te", "mis", "tus", "sus", "muy", "mas",
    "pero", "sin", "como", "cuando", "donde", "este", "esta", "estos",
    "estas", "ese", "esa", "esos", "esas", "aquel", "aquella",
})

GENERIC_TERMS = frozenset({
    "producto", "productos",
    "articulo", "articulos",
    "item", "items",
    "regalo", "regalos",
    "obsequio", "obsequios",
    "detalle", "detalles",
    "cosa", "cosas",
})

SYNONYM_MAP: dict[str, str] = {
    "botilito": "BOTELLA", "botilitos": "BOTELLA",
    "botellon": "BOTELLA", "botellones": "BOTELLA",
    "botella": "BOTELLA", "botellas": "BOTELLA",
    "termo": "TERMO", "termos": "TERMO",
    "lapicero": "LAPICERO", "lapiceros": "LAPICERO",
    "esfero": "LAPICERO", "esferos": "LAPICERO",
    "boligrafo": "BOLIGRAFO", "boligrafos": "BOLIGRAFO",
    "pluma": "PLUMA", "plumas": "PLUMA",
    "lapiz": "LAPIZ", "lapices": "LAPIZ",
    "mug": "MUG", "mugs": "MUG",
    "taza": "MUG", "tazas": "MUG",
    "vaso": "VASO", "vasos": "VASO",
    "bolso": "BOLSO", "bolsos": "BOLSO",
    "mochila": "BOLSO", "mochilas": "BOLSO",
    "cartera": "BOLSO", "carteras": "BOLSO",
    "morral": "BOLSO", "morrales": "BOLSO",
    "agenda": "AGENDA", "agendas": "AGENDA",
    "libreta": "LIBRETA", "libretas": "LIBRETA",
    "cuaderno": "LIBRETA", "cuadernos": "LIBRETA",
    "block": "LIBRETA", "blocks": "LIBRETA",
    "usb": "USB", "memoria": "USB", "memorias": "USB",
    "cargador": "CARGADOR", "cargadores": "CARGADOR",
    "regalo": "REGALO", "regalos": "REGALO",
    "llavero": "LLAVERO", "llaveros": "LLAVERO",
    "gorra": "GORRA", "gorras": "GORRA",
    "visera": "GORRA", "viseras": "GORRA",
    "calculadora": "CALCULADORA", "calculadoras": "CALCULADORA",
    "paraguas": "PARAGUAS",
    "nevera": "NEVERA", "neveras": "NEVERA",
    "cooler": "NEVERA", "coolers": "NEVERA",
    "lonchera": "LONCHERA", "loncheras": "LONCHERA",
    "toalla": "TOALLA", "toallas": "TOALLA",
    "reloj": "RELOJ", "relojes": "RELOJ",
    "gafas": "GAFAS",
    "pulsera": "PULSERA", "pulseras": "PULSERA",
    "monedero": "MONEDERO", "monederos": "MONEDERO",
    "neceser": "NECESER", "neceseres": "NECESER",
    "mouse": "MOUSE", "raton": "MOUSE",
    "teclado": "TECLADO", "teclados": "TECLADO",
    "audifonos": "AUDIFONOS", "cascos": "AUDIFONOS",
    "hub": "HUB", "cable": "CABLE", "cables": "CABLE",
    "linterna": "LINTERNA", "linternas": "LINTERNA",
    "camisa": "ROPA", "camisas": "ROPA",
    "camiseta": "ROPA", "camisetas": "ROPA",
    "polo": "ROPA", "polos": "ROPA",
    "chaqueta": "ROPA", "chaquetas": "ROPA",
    "delantal": "ROPA", "delantales": "ROPA",
    "bolso_termico": "BOLSO_TERMICO",
    "nevera_portatil": "NEVERA",
    "organizador": "ORGANIZADOR", "organizadores": "ORGANIZADOR",
    "maleta": "MALETA", "maletas": "MALETA",
    "maletin": "MALETA", "maletines": "MALETA",
    "portafolio": "PORTAFOLIO", "portafolios": "PORTAFOLIO",
    "billetera": "BILLETERA", "billeteras": "BILLETERA",
    "tarjetero": "TARJETERO", "tarjeteros": "TARJETERO",
    "portatarjetas": "TARJETERO", "portacredencial": "TARJETERO",
}


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
