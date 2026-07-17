from ....shared.dictionaries.product_families import PRODUCT_EXPANSIONS
from ....shared.dictionaries.categories import CATEGORY_EXPANSIONS

MATERIAL_EXPANSIONS: dict[str, list[str]] = {
    "METAL": [
        "metal", "metalico", "acero", "inoxidable", "aluminio",
        "acero inoxidable", "metal cromado",
    ],
    "RPET": [
        "rpet", "pet reciclado", "plastico reciclado", "reciclado",
        "material reciclado",
    ],
    "BAMBU": [
        "bambu", "bamboo", "fibra bambu", "madera bambu",
    ],
    "CORCHO": [
        "corcho", "corcho natural", "corcho reciclado",
    ],
    "ALGODON": [
        "algodon", "algodon organico", "yute", "fibra natural",
    ],
    "MADERA": [
        "madera", "madera natural", "madera reciclada",
    ],
    "PLASTICO": [
        "plastico", "plastic", "polipropileno", "poliester",
    ],
    "VIDRIO": [
        "vidrio", "cristal", "vidrio templado",
    ],
    "CERAMICA": [
        "ceramica", "ceramic", "porcelana", "barro",
    ],
    "CUERO": [
        "cuero", "piel", "cuero sintetico",
    ],
    "SINTETICO": [
        "sintetico", "poliester", "nylon", "fibra sintetica",
    ],
    "POLIESTER": [
        "poliester", "sintetico", "fibra sintetica",
    ],
    "POLIPROPILENO": [
        "polipropileno", "plastico", "polimero",
    ],
    "NEOPRENO": [
        "neopreno", "material aislante",
    ],
    "SILICONA": [
        "silicona", "silicone", "material silicona",
    ],
    "CAUCHO": [
        "caucho", "goma", "material elastico",
    ],
    "TELA": [
        "tela", "textil", "tela corporativa",
    ],
    "YUTE": [
        "yute", "fibra natural", "algodon", "ecologico",
    ],
    "LONA": [
        "lona", "tela resistente", "material lona",
    ],
    "LIENZO": [
        "lienzo", "tela", "material artistico",
    ],
}

QUALITY_EXPANSIONS: list[str] = [
    "premium", "ejecutivo", "corporativo", "profesional",
    "alta calidad", "calidad superior", "fino", "excelente",
    "elegante", "distinguido", "exclusivo",
]

PRICE_LOW_EXPANSIONS: list[str] = [
    "economico", "barato", "accesible", "bajo costo",
    "promocional", "oferta", "descuento",
]

PRICE_HIGH_EXPANSIONS: list[str] = [
    "premium", "lujo", "alta gama", "exclusivo",
    "ejecutivo", "superior",
]

ECO_EXPANSIONS: list[str] = [
    "eco", "ecologico", "sostenible", "rpet", "bambu",
    "reciclado", "corcho", "algodon", "verde",
    "biodegradable", "organico", "natural",
]

ATTRIBUTE_EXPANSIONS: dict[str, list[str]] = {
    "PERSONALIZABLE": ["personalizable", "personalizado", "grabado", "bordado"],
    "ESTAMPADO": ["estampado", "impreso", "personalizado"],
    "LIGERO": ["ligero", "liviano", "compacto", "portatil"],
    "COMPACTO": ["compacto", "plegable", "portatil"],
    "PORTATIL": ["portatil", "compacto", "viajero", "plegable"],
    "PLEGABLE": ["plegable", "compacto", "portatil"],
    "REUTILIZABLE": ["reutilizable", "ecologico", "sostenible"],
    "RESISTENTE": ["resistente", "duradero", "fuerte", "robusto"],
    "IMPERMEABLE": ["impermeable", "agua", "resistente agua"],
    "TERMICO": ["termico", "aislante", "caliente", "frio"],
    "AISLANTE": ["aislante", "termico", "frio", "caliente"],
    "GRABADO": ["grabado", "personalizado", "bordado", "logotipo"],
    "BORDADO": ["bordado", "logotipo", "personalizado"],
}

COLOR_EXPANSIONS: dict[str, list[str]] = {
    "NEGRO": ["negro", "black", "oscuro", "carbon"],
    "BLANCO": ["blanco", "white", "claro", "neutro"],
    "AZUL": ["azul", "blue", "marino", "celeste"],
    "ROJO": ["rojo", "red", "escarlata", "carmesi"],
    "VERDE": ["verde", "green", "bosque", "esmeralda"],
    "GRIS": ["gris", "gray", "plateado", "carbono"],
    "PLATEADO": ["plateado", "silver", "metalico", "gris"],
    "DORADO": ["dorado", "gold", "amarillo oro"],
    "AMARILLO": ["amarillo", "yellow"],
    "NARANJA": ["naranja", "orange"],
    "MORADO": ["morado", "purple", "violeta"],
    "ROSA": ["rosa", "pink", "rosado"],
    "CAFE": ["cafe", "marron", "brown", "tierra"],
    "BEIGE": ["beige", "crema", "natural"],
    "TRANSPARENTE": ["transparente", "cristal", "vidrio"],
}
