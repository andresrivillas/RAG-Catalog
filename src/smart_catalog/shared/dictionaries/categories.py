# ──────────────────────────────────────────────
# Única fuente de verdad para categorías del catálogo
# ──────────────────────────────────────────────

CANONICAL_CATEGORIES: set[str] = {
    "Tecnologia", "Oficina", "Hogar", "Viaje", "Deportes",
    "Eco", "Textil", "Bolsos", "Termos", "Bebidas",
    "Escritura", "Accesorios", "Libretas", "Escolar",
    "Salud", "Belleza", "Moda", "Musica", "Juguetes",
    "Herramientas", "Libros",
}

# ──────────────────────────────────────────────
# Sinónimos: término normalizado → categoría canónica
# Usado por: QueryUnderstanding
# ──────────────────────────────────────────────
CATEGORY_KEYWORDS: dict[str, str] = {
    "tecnologia": "Tecnologia",
    "tecnologico": "Tecnologia",
    "electronica": "Tecnologia",
    "informatica": "Tecnologia",
    "computacion": "Tecnologia",
    "oficina": "Oficina",
    "escritorio": "Oficina",
    "hogar": "Hogar",
    "cocina": "Hogar",
    "jardin": "Hogar",
    "viaje": "Viaje",
    "bebidas": "Bebidas",
    "escritura": "Escritura",
    "textil": "Textil",
    "ropa": "Textil",
    "accesorios": "Accesorios",
    "libretas": "Libretas",
    "bolsos": "Bolsos",
    "eco": "Eco",
    "ecologico": "Eco",
    "ecologica": "Eco",
    "ecologicos": "Eco",
    "ecologicas": "Eco",
    "sostenible": "Eco",
    "reciclado": "Eco",
    "reciclada": "Eco",
    "biodegradable": "Eco",
    "termos": "Termos",
    "deportes": "Deportes",
    "deportivo": "Deportes",
    "musica": "Musica",
    "herramientas": "Herramientas",
    "juguetes": "Juguetes",
    "libros": "Libros",
    "salud": "Salud",
    "belleza": "Belleza",
    "cuidado_personal": "Belleza",
    "moda": "Moda",
    "escolar": "Escolar",
    "universidad": "Escolar",
}

# ──────────────────────────────────────────────
# Expansiones semánticas: categoría → términos de búsqueda
# Usado por: SemanticQueryExpansion
# ──────────────────────────────────────────────
CATEGORY_EXPANSIONS: dict[str, list[str]] = {
    "Eco": [
        "eco", "ecologico", "sostenible", "rpet", "bambu",
        "reciclado", "reciclable", "corcho", "algodon",
        "biodegradable", "material reciclado",
    ],
    "Tecnologia": [
        "tecnologia", "electronico", "digital", "cargador",
        "usb", "inalambrico", "cable", "accesorio electronico",
    ],
    "Oficina": [
        "oficina", "escritorio", "organizador", "papeleria",
        "lapicero", "agenda", "calculadora", "accesorio oficina",
    ],
    "Termos": [
        "termo", "termico", "aislante", "caliente", "frio",
        "botella termica",
    ],
    "Bolsos": [
        "bolso", "bolsa", "mochila", "cartera", "accesorio",
        "bolsa corporativa",
    ],
    "Hogar": [
        "hogar", "casa", "cocina", "decoracion",
        "accesorio hogar", "utilidad hogar",
    ],
    "Viaje": [
        "viaje", "viajero", "maleta", "accesorio viaje",
        "neceser", "organizador viaje",
    ],
    "Escritura": [
        "escritura", "lapicero", "lapiz", "boligrafo", "esfero",
        "pluma", "marcador", "resaltador",
    ],
    "Textil": [
        "textil", "ropa", "camisa", "camiseta", "polo",
        "uniforme", "vestuario corporativo",
    ],
    "Accesorios": [
        "accesorio", "complemento", "detalle",
    ],
    "Libretas": [
        "libreta", "cuaderno", "agenda", "block", "papeleria",
        "libreta corporativa",
    ],
    "Deportes": [
        "deporte", "deportivo", "accesorio deportivo",
        "toalla", "gorra", "botella deportiva",
    ],
    "Musica": [
        "musica", "audifonos", "parlante", "accesorio musica",
    ],
    "Juguetes": [
        "juguete", "peluche", "juego", "didactico",
    ],
    "Salud": [
        "salud", "bienestar", "cuidado personal", "masajeador",
    ],
    "Belleza": [
        "belleza", "cosmetica", "cuidado personal", "espejo",
    ],
    "Moda": [
        "moda", "accesorio moda", "ropa", "complemento",
    ],
    "Escolar": [
        "escolar", "universidad", "estudiante", "papeleria",
        "utiles escolares", "mochila escolar",
    ],
    "Herramientas": [
        "herramienta", "multiusos", "utilidad", "kit herramientas",
    ],
}
