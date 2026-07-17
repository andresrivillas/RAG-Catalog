SIGNAL_MATERIAL_PREMIUM: dict[str, float] = {
    "acero inoxidable": 0.40, "cuero": 0.40, "metal": 0.30,
    "vidrio": 0.30, "ceramica": 0.30, "madera": 0.25,
    "aluminio": 0.20, "porcelana": 0.35, "cristal": 0.30,
    "poliéster": 0.05, "plastico": 0.0, "plástico": 0.0,
    "pvc": 0.0, "eva": 0.0, "cartón": 0.0,
}

SIGNAL_MATERIAL_ECO: dict[str, float] = {
    "rpet": 0.50, "bambú": 0.50, "bambu": 0.50,
    "corcho": 0.40, "algodón": 0.30, "algodon": 0.30,
    "reciclado": 0.45, "cartón": 0.25, "carton": 0.25,
    "yute": 0.35, "trigo": 0.30, "madera": 0.20,
    "metal": 0.05, "acero inoxidable": 0.05,
}

SIGNAL_MATERIAL_TECH: dict[str, float] = {
    "silicona": 0.10, "poliéster": 0.05,
}

SIGNAL_MATERIAL_LUXURY: dict[str, float] = {
    "cuero": 0.50, "metal": 0.20, "madera": 0.25,
    "vidrio": 0.25, "ceramica": 0.25, "porcelana": 0.30,
    "cristal": 0.25, "acero inoxidable": 0.25,
}

SIGNAL_MATERIAL_EXECUTIVE: dict[str, float] = {
    "cuero": 0.30, "acero inoxidable": 0.20,
    "metal": 0.15, "madera": 0.15,
}

SIGNAL_NAME_PREMIUM: dict[str, float] = {
    "premium": 0.50, "luxury": 0.50, "lux": 0.40,
    "elite": 0.30, "executive": 0.30,
    "platinium": 0.40, "gold": 0.30, "master": 0.20,
}

SIGNAL_NAME_ECO: dict[str, float] = {
    "eco": 0.45, "eco friendly": 0.50, "ecofriendly": 0.50,
    "ecologico": 0.50, "sostenible": 0.45,
    "reciclado": 0.40, "reciclable": 0.35,
    "verde": 0.25, "natural": 0.20,
    "rpet": 0.50, "bambu": 0.45, "cork": 0.35,
    "green": 0.30, "organic": 0.30, "organico": 0.30,
}

SIGNAL_NAME_TECH: dict[str, float] = {
    "bluetooth": 0.60, "wireless": 0.55, "inalambrico": 0.55,
    "usb": 0.40, "digital": 0.35, "smart": 0.50,
    "tech": 0.35, "tecnologia": 0.30,
    "cargador": 0.30, "power bank": 0.50, "powerbank": 0.50,
    "carga": 0.20, "recargable": 0.30,
    "led": 0.25, "luz": 0.15, "uv": 0.30,
    "wifi": 0.50, "electronico": 0.30,
    "computacion": 0.25, "mouse": 0.20,
    "audifonos": 0.25, "cascos": 0.20,
}

SIGNAL_NAME_EXECUTIVE: dict[str, float] = {
    "ejecutivo": 0.45, "executive": 0.45,
    "corporativo": 0.30, "profesional": 0.25,
    "directivo": 0.30, "gerente": 0.20,
    "oficina": 0.15, "empresarial": 0.20,
}

SIGNAL_NAME_LUXURY: dict[str, float] = {
    "luxury": 0.55, "lux": 0.45, "gold": 0.35,
    "platinium": 0.40, "elite": 0.30,
    "diamante": 0.45, "rubi": 0.30,
}

SIGNAL_NAME_INNOVATION: dict[str, float] = {
    "smart": 0.45, "digital": 0.30, "innovacion": 0.40,
    "nuevo": 0.15, "new": 0.15,
    "tecnologia": 0.25, "tech": 0.30,
    "bluetooth": 0.40, "wireless": 0.40,
    "uv": 0.35, "led": 0.20, "solar": 0.35,
}

SIGNAL_TAG_PREMIUM: dict[str, float] = {
    "premium": 0.40, "alta gama": 0.40, "alta_gama": 0.40,
    "exclusivo": 0.35, "lujo": 0.45, "exclusividad": 0.30,
}

SIGNAL_TAG_ECO: dict[str, float] = {
    "eco": 0.40, "ecologico": 0.45, "sostenible": 0.40,
    "reciclado": 0.35, "verde": 0.20, "green": 0.30,
    "biodegradable": 0.35, "organico": 0.30,
}

SIGNAL_TAG_TECH: dict[str, float] = {
    "tecnologico": 0.35, "electronico": 0.30, "digital": 0.30,
    "accesorio electronico": 0.20, "informatica": 0.25,
}

SIGNAL_TAG_EXECUTIVE: dict[str, float] = {
    "ejecutivo": 0.35, "corporativo": 0.25, "profesional": 0.20,
}

SIGNAL_TAG_INDUSTRY: dict[str, dict[str, float]] = {
    "tecnologia": {"TECNOLOGIA": 0.30},
    "electronica": {"TECNOLOGIA": 0.30},
    "tecnologico": {"TECNOLOGIA": 0.25},
    "deportes": {"DEPORTES": 0.30},
    "deportivo": {"DEPORTES": 0.25},
    "medico": {"SALUD": 0.35},
    "salud": {"SALUD": 0.30},
    "eco": {"ECO": 0.30, "EDUCACION": 0.15},
    "ecologico": {"ECO": 0.30},
    "oficina": {"OFICINA": 0.30, "CORPORATIVO": 0.20},
    "corporativo": {"CORPORATIVO": 0.25},
    "ejecutivo": {"CORPORATIVO": 0.20},
    "viaje": {"VIAJES": 0.30},
    "viajero": {"VIAJES": 0.25},
    "escolar": {"EDUCACION": 0.30},
    "universidad": {"EDUCACION": 0.25},
}

SIGNAL_CATEGORY_INDUSTRY: dict[str, dict[str, float]] = {
    "tecnologia": {"TECNOLOGIA": 0.40, "TELECOMUNICACIONES": 0.20, "STARTUPS": 0.15},
    "oficina": {"OFICINA": 0.40, "CORPORATIVO": 0.30},
    "deportes": {"DEPORTES": 0.40, "OUTDOOR": 0.15},
    "hogar": {"HOGAR": 0.30, "CORPORATIVO": 0.10},
    "eco": {"ECO": 0.40, "EDUCACION": 0.20, "CONSULTORIA": 0.15},
    "textil": {"TEXTIL": 0.30, "CORPORATIVO": 0.20, "MODA": 0.15},
    "bolsos": {"VIAJES": 0.30, "CORPORATIVO": 0.25},
    "termos": {"ARQUITECTURA": 0.20, "INGENIERIA": 0.15, "CONSTRUCCION": 0.15, "OFICINA": 0.25},
    "viaje": {"VIAJES": 0.40},
    "escritura": {"EDUCACION": 0.30, "OFICINA": 0.25},
    "libretas": {"EDUCACION": 0.30, "OFICINA": 0.25, "CONSULTORIA": 0.15},
    "escolar": {"EDUCACION": 0.35},
    "bebidas": {"OFICINA": 0.30, "EVENTOS": 0.25},
    "accesorios": {"CORPORATIVO": 0.20, "EVENTOS": 0.20},
    "salud": {"SALUD": 0.40, "BIENESTAR": 0.25},
    "belleza": {"SALUD": 0.25, "BIENESTAR": 0.30},
    "moda": {"MODA": 0.35, "CORPORATIVO": 0.10},
}

SIGNAL_NAME_INDUSTRY: dict[str, dict[str, float]] = {
    "arquitectura": {"ARQUITECTURA": 0.25}, "arquitectonico": {"ARQUITECTURA": 0.20},
    "construccion": {"CONSTRUCCION": 0.25}, "constructora": {"CONSTRUCCION": 0.20},
    "ingenieria": {"INGENIERIA": 0.25}, "industrial": {"INGENIERIA": 0.15, "INDUSTRIAL": 0.20},
    "smart": {"TECNOLOGIA": 0.20, "INNOVACION": 0.15},
    "bluetooth": {"TECNOLOGIA": 0.30, "TELECOMUNICACIONES": 0.15},
    "digital": {"TECNOLOGIA": 0.25}, "usb": {"TECNOLOGIA": 0.25},
    "medico": {"SALUD": 0.30}, "salud": {"SALUD": 0.20},
    "hospital": {"SALUD": 0.25}, "clinica": {"SALUD": 0.20},
    "educacion": {"EDUCACION": 0.25}, "colegio": {"EDUCACION": 0.25},
    "universidad": {"EDUCACION": 0.25}, "estudiante": {"EDUCACION": 0.20},
    "banco": {"FINANCIERO": 0.25}, "financiero": {"FINANCIERO": 0.25},
    "seguro": {"FINANCIERO": 0.20}, "legal": {"LEGAL": 0.25},
    "abogado": {"LEGAL": 0.25}, "juridico": {"LEGAL": 0.20},
    "deporte": {"DEPORTES": 0.25}, "fitness": {"DEPORTES": 0.25},
    "gym": {"DEPORTES": 0.25}, "viaje": {"VIAJES": 0.25},
    "travel": {"VIAJES": 0.20}, "turismo": {"VIAJES": 0.20},
    "evento": {"EVENTOS": 0.25}, "feria": {"EVENTOS": 0.20},
}

SIGNAL_NAME_CUSTOMER: dict[str, dict[str, float]] = {
    "ejecutivo": {"EJECUTIVO": 0.35}, "executive": {"EJECUTIVO": 0.35},
    "vip": {"VIP": 0.35}, "profesional": {"PROFESIONAL": 0.25},
    "corporativo": {"EJECUTIVO": 0.15, "ADMINISTRATIVO": 0.15},
    "gerente": {"EJECUTIVO": 0.30}, "directivo": {"EJECUTIVO": 0.30},
    "ceo": {"EJECUTIVO": 0.35, "VIP": 0.20},
    "estudiante": {"ESTUDIANTE": 0.30}, "universitario": {"ESTUDIANTE": 0.25},
    "deportista": {"DEPORTISTA": 0.30}, "atleta": {"DEPORTISTA": 0.25},
    "viajero": {"VIAJERO": 0.30}, "comercial": {"COMERCIAL": 0.25},
    "empresarial": {"EJECUTIVO": 0.20, "COMERCIAL": 0.20},
    "administrativo": {"ADMINISTRATIVO": 0.25},
    "asistente": {"ADMINISTRATIVO": 0.20},
    "tecnologico": {"TECNOLOGICO": 0.25},
}

SIGNAL_NAME_OCCASION: dict[str, dict[str, float]] = {
    "bienvenida": {"BIENVENIDA": 0.30},
    "evento": {"EVENTOS": 0.25}, "eventos": {"EVENTOS": 0.25},
    "feria": {"FERIAS": 0.30}, "ferias": {"FERIAS": 0.30},
    "capacitacion": {"CAPACITACION": 0.25},
    "conferencia": {"CONFERENCIAS": 0.25}, "congreso": {"CONGRESOS": 0.25},
    "lanzamiento": {"LANZAMIENTOS": 0.25},
    "premio": {"PREMIOS": 0.25}, "reconocimiento": {"RECONOCIMIENTO": 0.25},
    "viaje": {"VIAJES": 0.20},
    "workshop": {"WORKSHOP": 0.25},
    "reunion": {"REUNIONES": 0.20},
}

SIGNAL_NAME_CAMPAIGN: dict[str, dict[str, float]] = {
    "lanzamiento": {"LANZAMIENTO": 0.25},
    "promocional": {"PROMOCIONAL": 0.25},
    "evento": {"EVENTO_CORPORATIVO": 0.20},
    "corporativo": {"EVENTO_CORPORATIVO": 0.20},
    "feria": {"FERIA": 0.25},
    "capacitacion": {"CAPACITACION": 0.20},
    "bienvenida": {"BIENVENIDA": 0.20},
}

PRICE_POSITION_THRESHOLDS: list[tuple[float, str]] = [
    (0.90, "muy_alto"),
    (0.75, "alto"),
    (0.50, "medio_alto"),
    (0.25, "medio"),
    (0.0, "bajo"),
]

COMMERCIAL_VALUE_THRESHOLDS: dict[str, tuple[float, float]] = {
    "high_value": (0.25, 1.0),
    "valuable": (0.15, 0.25),
    "standard": (0.08, 0.15),
    "economic": (0.0, 0.08),
}

DIFFERENTIATOR_KEYWORDS: dict[str, list[str]] = {
    "doble pared": ["doble pared", "termico", "aislante"],
    "recargable": ["recargable", "rechargeable", "carga usb"],
    "inalambrico": ["inalambrico", "wireless", "bluetooth"],
    "ecologico": ["ecologico", "sostenible", "reciclado", "rpet", "bambu"],
    "tecnologico": ["smart", "digital", "bluetooth", "usb", "tech"],
    "premium": ["premium", "luxury", "elite", "exclusivo"],
    "multifuncional": ["multifuncional", "multiusos", "2 en 1", "3 en 1"],
    "portatil": ["portatil", "compacto", "viajero", "plegable"],
    "personalizable": ["personalizable", "personalizado", "grabado"],
}

INFERRED_ATTRIBUTE_THRESHOLDS: dict[str, list[tuple[float, str]]] = {
    "premium_level": [
        (0.40, "luxury"), (0.25, "premium"),
        (0.12, "standard"), (0.0, "basic"),
    ],
    "eco_level": [
        (0.40, "muy_alto"), (0.25, "alto"),
        (0.12, "medio"), (0.0, "bajo"),
    ],
    "technology_level": [
        (0.35, "muy_alto"), (0.20, "alto"),
        (0.10, "medio"), (0.0, "bajo"),
    ],
    "executive_level": [
        (0.30, "alto"), (0.15, "medio"), (0.0, "bajo"),
    ],
    "luxury_level": [
        (0.35, "muy_alto"), (0.20, "alto"),
        (0.10, "medio"), (0.0, "bajo"),
    ],
    "innovation_level": [
        (0.30, "muy_alto"), (0.18, "alto"),
        (0.08, "medio"), (0.0, "bajo"),
    ],
    "practicality_level": [
        (0.20, "muy_alto"), (0.10, "alto"),
        (0.05, "medio"), (0.0, "bajo"),
    ],
    "commercial_value": [
        (0.30, "high_value"), (0.18, "valuable"),
        (0.10, "standard"), (0.0, "economic"),
    ],
    "corporate_affinity": [
        (0.30, "alta"), (0.15, "media"), (0.0, "baja"),
    ],
}
