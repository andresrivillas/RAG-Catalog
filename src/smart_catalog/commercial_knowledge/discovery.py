COMMERCIAL_COLLECTIONS: dict[str, dict] = {
    "para_ejecutivos": {
        "title": "Productos para Ejecutivos",
        "icon": "💼",
        "query": "ejecutivo profesional corporativo gerente directivo oficina premium",
        "description": "Productos seleccionados para perfiles ejecutivos y directivos",
    },
    "para_arquitectura": {
        "title": "Productos para Arquitectura",
        "icon": "🏛️",
        "query": "arquitectura construccion diseño moderno botella termo agenda estilo",
        "description": "Recomendados para firmas de arquitectura y construcción",
    },
    "para_tecnologia": {
        "title": "Productos para Tecnología",
        "icon": "💻",
        "query": "tecnologia startup innovacion digital usb audifonos powerbank moderno",
        "description": "Ideales para empresas de tecnología y startups",
    },
    "para_constructoras": {
        "title": "Productos para Constructoras",
        "icon": "🏗️",
        "query": "construccion obra industria botella termo nevera practico resistente",
        "description": "Recomendados para constructoras e industria pesada",
    },
    "para_educacion": {
        "title": "Productos para Educación",
        "icon": "📚",
        "query": "educacion universidad escolar capacitacion agenda libreta lapicero",
        "description": "Ideales para instituciones educativas",
    },
    "para_eventos": {
        "title": "Productos para Eventos",
        "icon": "🎪",
        "query": "evento feria convencion congreso promocional llavero usb gorra",
        "description": "Perfectos para ferias, congresos y eventos corporativos",
    },
    "para_bienvenida": {
        "title": "Productos para Bienvenida",
        "icon": "🤝",
        "query": "bienvenida corporativo kit inicio botella termo libreta agenda mochila",
        "description": "Kits de bienvenida para nuevos empleados o clientes",
    },
    "para_clientes_vip": {
        "title": "Productos para Clientes VIP",
        "icon": "⭐",
        "query": "vip exclusivo premium lujo ejecutivo reloj termo maletin audifonos",
        "description": "Regalos exclusivos para clientes VIP",
    },
    "para_salud": {
        "title": "Productos para el Sector Salud",
        "icon": "🏥",
        "query": "salud medico hospital bienestar botella toalla termo util practico",
        "description": "Recomendados para clínicas, hospitales y profesionales de la salud",
    },
    "para_financiero": {
        "title": "Productos para el Sector Financiero",
        "icon": "🏦",
        "query": "financiero banco seguros ejecutivo corporativo agenda calculadora paraguas",
        "description": "Ideales para bancos, seguros y el sector financiero",
    },
}


def get_commercial_collections() -> list[dict]:
    return [
        {"key": key, **info}
        for key, info in COMMERCIAL_COLLECTIONS.items()
    ]
