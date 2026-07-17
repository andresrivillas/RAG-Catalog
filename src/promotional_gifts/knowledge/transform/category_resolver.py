import re
import unicodedata
from typing import List, Tuple

from ...domain.entities.product_knowledge import ProductKnowledge


CANONICAL_CATEGORIES = {
    "tecnología", "oficina", "viaje", "hogar", "eco", "bebidas", "textiles",
    "herramientas", "maletines", "termos", "libretas", "escritura", "bolsos",
    "salud", "eventos", "deportes", "accesorios", "limpieza", "juegos", "otros",
}

# Alias exactos que pueden venir del Excel o del breadcrumb.
CATEGORY_ALIASES = {
    "tecnologia": "Tecnología",
    "tecnología": "Tecnología",
    "tech": "Tecnología",
    "electronica": "Tecnología",
    "electrónica": "Tecnología",
    "usb": "Tecnología",
    "oficina": "Oficina",
    "escritorio": "Oficina",
    "papeleria": "Oficina",
    "papelería": "Oficina",
    "viaje": "Viaje",
    "viajes": "Viaje",
    "travel": "Viaje",
    "hogar": "Hogar",
    "casa": "Hogar",
    "cocina": "Hogar",
    "kitchen": "Hogar",
    "eco": "Eco",
    "ecologico": "Eco",
    "ecológico": "Eco",
    "sostenible": "Eco",
    "reciclado": "Eco",
    "bebidas": "Bebidas",
    "drink": "Bebidas",
    "textiles": "Textiles",
    "textil": "Textiles",
    "camisetas": "Textiles",
    "gorras": "Textiles",
    "herramientas": "Herramientas",
    "herramienta": "Herramientas",
    "maletines": "Maletines",
    "maletin": "Maletines",
    "maletín": "Maletines",
    "termos": "Termos",
    "termo": "Termos",
    "libretas": "Libretas",
    "libreta": "Libretas",
    "escritura": "Escritura",
    "lapiceros": "Escritura",
    "boligrafos": "Escritura",
    "bolígrafos": "Escritura",
    "bolsos": "Bolsos",
    "bolsa": "Bolsos",
    "salud": "Salud",
    "bienestar": "Salud",
    "eventos": "Eventos",
    "ferias": "Eventos",
    "deportes": "Deportes",
    "deporte": "Deportes",
    "fitness": "Deportes",
    "gym": "Deportes",
    "accesorios": "Accesorios",
    "limpieza": "Limpieza",
    "otros": "Otros",
    "varios": "Otros",
    "mascotas": "Otros",
    "juguetes": "Otros",
}

# Reglas de inferencia por palabra clave. El orden importa: las primeras tienen
# prioridad cuando varias categorías compiten.
CATEGORY_RULES: List[Tuple[str, List[str]]] = [
    ("Termos", ["termo", "termos", "cantimplora", "botella térmica", "botella termica", "termica", "térmica"]),
    ("Escritura", ["bolígrafo", "boligrafo", "pluma", "marcador", "resaltador", "lapicero", "portaminas", "tinta", "roller", "escritura", "lápiz", "lapiz"]),
    ("Libretas", ["libreta", "cuaderno", "agenda", "anotador", "planner", "diario"]),
    ("Tecnología", ["usb", "cargador", "cable", "power bank", "powerbank", "batería", "bateria", "auricular", "audífonos", "audifonos", "altavoz", "parlante", "bluetooth", "mouse", "ratón", "teclado", "soporte móvil", "soporte movil", "celular", "móvil", "movil", "gadget", "adaptador", "hub usb", "memoria usb", "pendrive", "memoria", "tech", "tecnologico", "tecnológico", "digital"]),
    ("Maletines", ["maletín", "maletin", "maleta ejecutiva", "portafolio", "portadocumentos"]),
    ("Viaje", ["maleta", "mochila", "bolso de viaje", "neceser", "pasaporte", "tag de maleta", "paraguas", "viajero"]),
    ("Bolsos", ["bolso", "bolsa", "tote", "morral", "lonchera"]),
    ("Hogar", ["taza", "mug", "vaso", "plato", "cuchara", "cocina", "cafetera", "hervidor", "reloj", "alarma", "ambientador", "cojín", "cojin", "almohada", "toalla", "mantel", "set de cocina", "portacomidas", "portavasos", "aspiradora", "abanico", "portarretrato", "almanaque", "botilito", "coca", "coca cola", "galleta", "chocolate", "termo"]),
    ("Oficina", ["oficina", "escritorio", "organizador", "clipboard", "porta documentos", "sujetapapeles", "clips", "pegamento", "calculadora", "perforadora", "engrapadora", "tijeras", "cinta adhesiva", "post-it", "notas adhesivas"]),
    ("Bebidas", ["bebida", "botella", "cantimplora", "copas", "vaso", "botilito", "coca", "coca cola", "termo", "cafetera"]),
    ("Eco", ["eco", "ecológico", "ecologico", "sostenible", "reciclado", "reciclable", "rpet", "bambú", "bambu", "corcho", "paja", "trigo", "yute", "algodón", "algodon", "natural"]),
    ("Textiles", ["camiseta", "polo", "camisa", "gorra", "sombrero", "bufanda", "guante", "mascarilla", "bandana", "cinta", "lanyard", "corbata", "bolsa textil", "mochila textil", "balaca", "cinta para maquillaje", "pañoleta", "bolsa"]),
    ("Herramientas", ["destornillador", "llave", "navaja", "multiherramienta", "linterna", "cinta métrica", "cinta metrica", "nivel", "martillo", "alicate", "herramienta", "metro", "regla", "llavero", "destapador"]),
    ("Salud", ["botiquín", "botiquin", "tapabocas", "termómetro", "antibacterial", "desinfectante", "higiene", "toalla deportiva", "botella deportiva", "salud"]),
    ("Deportes", ["gimnasio", "balón", "pelota", "raqueta", "bici", "bicicleta", "ciclismo", "botella deportiva", "toalla deportiva", "deporte"]),
    ("Eventos", ["feria", "congreso", "conferencia", "merchandising", "stand", "exposición", "exposicion", "brindis", "celebración", "celebracion", "evento"]),
    ("Juegos", ["juego", "tangram", "triqui", "desestresante", "rompecabezas", "puzzle", "dado", "cartas", "naipes"]),
]


class CategoryResolver:
    """Resuelve categoría y subcategoría canónicas de forma determinista."""

    def resolve(self, product: ProductKnowledge) -> Tuple[str, str]:
        category, subcategory = "", ""

        # 1. Breadcrumb (último segmento significativo antes del nombre).
        if product.breadcrumb:
            category, subcategory = self._from_breadcrumb(product.breadcrumb)
            if category:
                return category, subcategory

        # 2. category si ya está limpia.
        if product.category:
            category, subcategory = self._from_clean_value(product.category)
            if category:
                return category, subcategory

        # 3. excel_category (reservado para futura importación directa).
        if product.excel_category:
            category, subcategory = self._from_clean_value(product.excel_category)
            if category:
                return category, subcategory

        # 4. Inferencia combinada: nombre, descripción, materiales, beneficios,
        # características, personalización y etiquetas. Usamos más campos que
        # solo el nombre para reducir la categoría "Otros" en productos cuya
        # descripción sí contiene señales claras.
        combined_text = self._combine_fields(product)
        category, subcategory = self._from_text(combined_text)
        if category:
            return category, subcategory

        return "Otros", ""

    def _combine_fields(self, product: ProductKnowledge) -> str:
        fields = [
            product.name,
            product.description,
            product.characteristics,
            product.benefits,
            product.materials,
            product.customization,
        ]
        tags = list(product.commercial_tags) + list(product.audience_tags) + list(product.occasion_tags)
        return " ".join(fields + tags).strip()

    def _from_breadcrumb(self, breadcrumb: str) -> Tuple[str, str]:
        parts = [
            p.strip()
            for p in re.split(r"\s*>\s*|\s*/\s*|\s*\\\s*", breadcrumb)
            if p.strip()
        ]
        ignore = {"inicio", "home", "productos", "catálogo", "catalogo", "tienda"}
        parts = [p for p in parts if self._normalize(p) not in ignore]
        if not parts:
            return "", ""
        category = self._map_alias(parts[-1])
        subcategory = self._map_alias(parts[-2]) if len(parts) >= 2 else ""
        if category:
            return category, subcategory
        # Si el último segmento no es alias exacto, intentar keyword matching.
        category = self._category_from_text(parts[-1])
        if not category and len(parts) >= 2:
            category = self._category_from_text(parts[-2])
        if category and not subcategory and len(parts) >= 2:
            subcategory = self._title(parts[-2])
        return category, subcategory

    def _from_clean_value(self, value: str) -> Tuple[str, str]:
        value = value.strip()
        if len(value) > 60 or "\n" in value or ">" in value or "|" in value:
            return "", ""
        # Si parece texto de menú, rechazar.
        menu_terms = {"menú", "menu", "categorías", "categorias", "ver todo", "ver todos"}
        if any(term in self._normalize(value) for term in menu_terms):
            return "", ""
        category = self._map_alias(value)
        if category:
            return category, ""
        return self._category_from_text(value), ""

    def _from_text(self, text: str) -> Tuple[str, str]:
        category = self._category_from_text(text)
        subcategory = ""
        if category:
            subcategory = self._first_matching_keyword(text, category)
        return category, subcategory

    def _category_from_text(self, text: str) -> str:
        norm = self._normalize(text)
        for category, keywords in CATEGORY_RULES:
            for kw in keywords:
                if self._normalize(kw) in norm:
                    return category
        return ""

    def _first_matching_keyword(self, text: str, category: str) -> str:
        norm = self._normalize(text)
        for cat, keywords in CATEGORY_RULES:
            if cat != category:
                continue
            for kw in keywords:
                nkw = self._normalize(kw)
                if nkw in norm:
                    return self._title(kw)
        return ""

    def _map_alias(self, text: str) -> str:
        return CATEGORY_ALIASES.get(self._normalize(text).strip(), "")

    @staticmethod
    def _normalize(text: str) -> str:
        if not text:
            return ""
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        return re.sub(r"[^a-z0-9\s]", " ", text.lower()).strip()

    @staticmethod
    def _title(text: str) -> str:
        if not text:
            return ""
        return " ".join(word.capitalize() for word in text.split())
