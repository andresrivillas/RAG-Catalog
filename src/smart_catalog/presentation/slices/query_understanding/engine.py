import logging
import re
import unicodedata
from typing import Optional

from ....domain.models.structured_search_query import StructuredSearchQuery

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
    "articulo", "articulos",
    "cosa", "cosas",
})

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

MATERIAL_KEYWORDS: dict[str, str] = {
    "metalico": "METAL",
    "metalica": "METAL",
    "metal": "METAL",
    "metalica": "METAL",
    "metalicos": "METAL",
    "metalicas": "METAL",
    "acero": "METAL",
    "inoxidable": "METAL",
    "aluminio": "METAL",
    "rpet": "RPET",
    "bambu": "BAMBU",
    "corcho": "CORCHO",
    "algodon": "ALGODON",
    "madera": "MADERA",
    "plastico": "PLASTICO",
    "plastica": "PLASTICO",
    "plasticos": "PLASTICO",
    "plasticas": "PLASTICO",
    "vidrio": "VIDRIO",
    "cristal": "VIDRIO",
    "ceramica": "CERAMICA",
    "porcelana": "CERAMICA",
    "cuero": "CUERO",
    "piel": "CUERO",
    "sintetico": "SINTETICO",
    "poliester": "POLIESTER",
    "polipropileno": "POLIPROPILENO",
    "neopreno": "NEOPRENO",
    "silicone": "SILICONA",
    "silicona": "SILICONA",
    "caucho": "CAUCHO",
    "goma": "CAUCHO",
    "tela": "TELA",
    "textil": "TELA",
    "yute": "YUTE",
    "yuta": "YUTE",
    "yute": "YUTE",
    "lona": "LONA",
    "lienzo": "LIENZO",
}

LOW_PRICE_KEYWORDS: frozenset = frozenset({
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

HIGH_PRICE_KEYWORDS: frozenset = frozenset({
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

QUALITY_KEYWORDS: frozenset = frozenset({
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

ECO_KEYWORDS: frozenset = frozenset({
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

CATEGORY_KEYWORDS: dict[str, str] = {
    "tecnologia": "Tecnologia",
    "tecnologico": "Tecnologia",
    "oficina": "Oficina",
    "hogar": "Hogar",
    "viaje": "Viaje",
    "bebidas": "Bebidas",
    "escritura": "Escritura",
    "textil": "Textil",
    "accesorios": "Accesorios",
    "libretas": "Libretas",
    "bolsos": "Bolsos",
    "eco": "Eco",
    "termos": "Termos",
    "cocina": "Hogar",
    "deportes": "Deportes",
    "deportivo": "Deportes",
    "musica": "Musica",
    "electronica": "Tecnologia",
    "informatica": "Tecnologia",
    "computacion": "Tecnologia",
    "escritorio": "Oficina",
    "cocina": "Hogar",
    "jardin": "Hogar",
    "herramientas": "Herramientas",
    "juguetes": "Juguetes",
    "libros": "Libros",
    "salud": "Salud",
    "belleza": "Belleza",
    "cuidado_personal": "Belleza",
    "moda": "Moda",
    "ropa": "Textil",
    "escolar": "Escolar",
    "universidad": "Escolar",
    "ecologico": "Eco",
    "ecologica": "Eco",
    "ecologicos": "Eco",
    "ecologicas": "Eco",
    "sostenible": "Eco",
    "reciclado": "Eco",
    "reciclada": "Eco",
    "biodegradable": "Eco",
}

COLOR_KEYWORDS: dict[str, str] = {
    "negro": "NEGRO",
    "negra": "NEGRO",
    "negros": "NEGRO",
    "negras": "NEGRO",
    "blanco": "BLANCO",
    "blanca": "BLANCO",
    "blancos": "BLANCO",
    "blancas": "BLANCO",
    "azul": "AZUL",
    "azules": "AZUL",
    "rojo": "ROJO",
    "roja": "ROJO",
    "rojos": "ROJO",
    "rojas": "ROJO",
    "verde": "VERDE",
    "verdes": "VERDE",
    "gris": "GRIS",
    "grises": "GRIS",
    "plateado": "PLATEADO",
    "plateada": "PLATEADO",
    "dorado": "DORADO",
    "dorada": "DORADO",
    "amarillo": "AMARILLO",
    "amarilla": "AMARILLO",
    "naranja": "NARANJA",
    "morado": "MORADO",
    "morada": "MORADO",
    "violeta": "MORADO",
    "rosa": "ROSA",
    "rosado": "ROSA",
    "rosada": "ROSA",
    "cafe": "CAFE",
    "marron": "CAFE",
    "marron": "CAFE",
    "beige": "BEIGE",
    "transparente": "TRANSPARENTE",
}

AUDIENCE_PATTERNS: list[tuple[str, str]] = [
    (r"para\s+medicos", "MEDICOS"),
    (r"para\s+doctor", "MEDICOS"),
    (r"para\s+enfermer", "MEDICOS"),
    (r"para\s+arquitectos", "ARQUITECTOS"),
    (r"para\s+ingenieros", "INGENIEROS"),
    (r"para\s+abogados", "ABOGADOS"),
    (r"para\s+profesores", "PROFESORES"),
    (r"para\s+maestros", "PROFESORES"),
    (r"para\s+docentes", "PROFESORES"),
    (r"para\s+ninos", "NINOS"),
    (r"para\s+ninas", "NINOS"),
    (r"para\s+universidad", "UNIVERSITARIOS"),
    (r"para\s+estudiantes", "ESTUDIANTES"),
    (r"para\s+empresa", "EMPRESA"),
    (r"para\s+empleados", "EMPRESA"),
    (r"para\s+corporativo", "EMPRESA"),
    (r"corporativos?", "EMPRESA"),
    (r"para\s+oficina", "OFICINA"),
    (r"eventos?", "EVENTOS"),
    (r"ferias?", "FERIAS"),
    (r"congresos?", "EVENTOS"),
    (r"convenciones?", "EVENTOS"),
    (r"lanzamiento", "LANZAMIENTO"),
    (r"cumpleanos", "CUMPLEANOS"),
    (r"boda", "BODA"),
    (r"regalos?\s+empresariales?", "EMPRESA"),
]

ATTRIBUTE_KEYWORDS: dict[str, str] = {
    "personalizable": "PERSONALIZABLE",
    "personalizado": "PERSONALIZABLE",
    "personalizados": "PERSONALIZABLE",
    "personalizada": "PERSONALIZABLE",
    "personalizadas": "PERSONALIZABLE",
    "estampado": "ESTAMPADO",
    "grabado": "GRABADO",
    "bordado": "BORDADO",
    "ligero": "LIGERO",
    "ligera": "LIGERO",
    "liviano": "LIGERO",
    "liviana": "LIGERO",
    "compacto": "COMPACTO",
    "compacta": "COMPACTO",
    "portatil": "PORTATIL",
    "plegable": "PLEGABLE",
    "reutilizable": "REUTILIZABLE",
    "resistente": "RESISTENTE",
    "impermeable": "IMPERMEABLE",
    "termico": "TERMICO",
    "termica": "TERMICO",
    "aislante": "AISLANTE",
}


class QueryUnderstandingEngine:

    def normalize_text(self, text: str) -> str:
        text = text.lower().strip()
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^a-z0-9\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def apply_synonyms(self, tokens: list[str]) -> list[str]:
        replaced = []
        for token in tokens:
            if token in PRODUCT_SYNONYMS:
                normalized = PRODUCT_SYNONYMS[token]
                replaced.append(normalized.lower())
                logger.debug("Sinonimo: %s -> %s", token, normalized)
            else:
                replaced.append(token)
        return replaced

    def detect_materials(self, tokens: list[str]) -> list[str]:
        detected = []
        for token in tokens:
            if token in MATERIAL_KEYWORDS:
                material = MATERIAL_KEYWORDS[token]
                if material not in detected:
                    detected.append(material)
                    logger.debug("Material detectado: %s (desde: %s)", material, token)
        return detected

    def detect_price_intent(self, tokens: list[str]) -> Optional[str]:
        for token in tokens:
            if token in LOW_PRICE_KEYWORDS:
                logger.debug("Intencion de precio baja: %s", token)
                return "LOW_PRICE"
        for token in tokens:
            if token in HIGH_PRICE_KEYWORDS:
                logger.debug("Intencion de precio alta: %s", token)
                return "HIGH_PRICE"
        return None

    def detect_quality_intent(self, tokens: list[str]) -> Optional[str]:
        for token in tokens:
            if token in QUALITY_KEYWORDS:
                logger.debug("Intencion de calidad: %s", token)
                return "HIGH_QUALITY"
        return None

    def detect_eco_intent(self, tokens: list[str]) -> bool:
        for token in tokens:
            if token in ECO_KEYWORDS:
                logger.debug("Intencion eco detectada: %s", token)
                return True
        return False

    def detect_categories(self, tokens: list[str]) -> list[str]:
        detected = []
        for token in tokens:
            if token in CATEGORY_KEYWORDS:
                cat = CATEGORY_KEYWORDS[token]
                if cat not in detected:
                    detected.append(cat)
                    logger.debug("Categoria detectada: %s (desde: %s)", cat, token)
        return detected

    def detect_colors(self, tokens: list[str]) -> list[str]:
        detected = []
        for token in tokens:
            if token in COLOR_KEYWORDS:
                color = COLOR_KEYWORDS[token]
                if color not in detected:
                    detected.append(color)
                    logger.debug("Color detectado: %s (desde: %s)", color, token)
        return detected

    def detect_audience(self, text: str) -> Optional[str]:
        for pattern, audience in AUDIENCE_PATTERNS:
            if re.search(pattern, text):
                logger.debug("Audiencia detectada: %s", audience)
                return audience
        return None

    def detect_attributes(self, tokens: list[str]) -> list[str]:
        detected = []
        for token in tokens:
            if token in ATTRIBUTE_KEYWORDS:
                attr = ATTRIBUTE_KEYWORDS[token]
                if attr not in detected:
                    detected.append(attr)
                    logger.debug("Atributo detectado: %s (desde: %s)", attr, token)
        return detected

    def detect_product_types(self, tokens: list[str]) -> list[str]:
        detected = []
        for token in tokens:
            if token in PRODUCT_SYNONYMS:
                ptype = PRODUCT_SYNONYMS[token]
                if ptype not in detected:
                    detected.append(ptype)
        return detected

    def calculate_confidence(
        self,
        tokens: list[str],
        known: int,
        product_types: list[str],
        materials: list[str],
        price_intent: Optional[str],
        categories: list[str],
    ) -> float:
        if not tokens:
            return 0.0

        score = 0.0
        total = len(tokens)

        if total > 0:
            score += 0.40 * (known / total)

        if product_types:
            score += 0.25 * min(1.0, len(product_types))
        if materials:
            score += 0.15 * min(1.0, len(materials))
        if price_intent:
            score += 0.10
        if categories:
            score += 0.10 * min(1.0, len(categories))

        return round(min(score, 1.0), 2)

    def understand(self, text: str) -> StructuredSearchQuery:
        start = __import__("time").perf_counter()

        original = text.strip()
        normalized = self.normalize_text(text)

        tokens = normalized.split()
        stop_words_removed = [t for t in tokens if t not in STOP_WORDS]
        content_tokens = [t for t in stop_words_removed if not t.isdigit()]

        product_types = self.detect_product_types(content_tokens)
        synonym_tokens = self.apply_synonyms(content_tokens)
        materials = self.detect_materials(content_tokens)
        price_intent = self.detect_price_intent(content_tokens)
        quality_intent = self.detect_quality_intent(content_tokens)
        eco_intent = self.detect_eco_intent(content_tokens)
        categories = self.detect_categories(content_tokens)
        colors = self.detect_colors(content_tokens)
        audience = self.detect_audience(normalized)
        attributes = self.detect_attributes(content_tokens)

        price_keywords = LOW_PRICE_KEYWORDS | HIGH_PRICE_KEYWORDS
        eco_keywords = ECO_KEYWORDS
        quality_keywords = QUALITY_KEYWORDS
        all_intent_keywords = price_keywords | eco_keywords | quality_keywords

        known_tokens: set[str] = set()

        for t in content_tokens:
            if t in PRODUCT_SYNONYMS:
                known_tokens.add(t)
            if t in MATERIAL_KEYWORDS:
                known_tokens.add(t)
            if t in CATEGORY_KEYWORDS:
                known_tokens.add(t)
            if t in COLOR_KEYWORDS:
                known_tokens.add(t)
            if t in ATTRIBUTE_KEYWORDS:
                known_tokens.add(t)
            if t in all_intent_keywords:
                known_tokens.add(t)

        for pat, _ in AUDIENCE_PATTERNS:
            match = re.search(pat, normalized)
            if match:
                for mt in match.group(0).split():
                    known_tokens.add(mt)

        known_count = len(known_tokens)
        unknown = [
            t for t in content_tokens
            if t not in known_tokens and t not in GENERIC_TERMS
        ]

        confidence = self.calculate_confidence(
            content_tokens, known_count, product_types, materials, price_intent, categories
        )

        normalized_query = " ".join(synonym_tokens)

        elapsed = (__import__("time").perf_counter() - start) * 1000

        logger.info(
            "Consulta original: '%s' | normalizada: '%s' | sinónimos aplicados: %s | "
            "materiales: %s | precio: %s | calidad: %s | eco: %s | categorías: %s | "
            "colores: %s | audiencia: %s | confianza: %.2f | tiempo: %.1fms",
            original, normalized_query,
            product_types, materials, price_intent, quality_intent, eco_intent,
            categories, colors, audience, confidence, elapsed,
        )

        return StructuredSearchQuery(
            original_query=original,
            normalized_query=normalized_query,
            detected_categories=categories,
            detected_materials=materials,
            detected_price_intent=price_intent,
            detected_quality_intent=quality_intent,
            detected_eco_intent=eco_intent,
            detected_product_types=product_types,
            detected_audience=audience,
            detected_colors=colors,
            detected_attributes=attributes,
            unknown_terms=unknown,
            confidence=confidence,
        )
