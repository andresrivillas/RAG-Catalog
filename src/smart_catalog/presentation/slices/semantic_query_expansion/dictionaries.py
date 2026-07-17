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
