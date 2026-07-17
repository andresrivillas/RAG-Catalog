from typing import Optional

AUDIENCE_RECOMMENDATIONS: dict[str, dict] = {
    "MEDICOS": {
        "preferred_families": ["BOTELLA", "TERMO", "AGENDA", "LAPICERO", "USB", "LLAVERO"],
        "preferred_categories": ["Salud", "Eco", "Oficina"],
        "preferred_materials": ["METAL", "BAMBU", "RPET", "ACERO_INOXIDABLE"],
        "preferred_attributes": ["IMPERMEABLE", "RESISTENTE", "PERSONALIZABLE"],
        "avoid_families": ["GORRA", "TOALLA", "PULSERA"],
        "avoid_categories": ["Juguetes", "Deportes"],
        "use_cases": ["CONGRESOS_MEDICOS", "CAPACITACION", "BIENVENIDA", "JORNADAS_SALUD"],
    },
    "ARQUITECTOS": {
        "preferred_families": ["BOTELLA", "TERMO", "AGENDA", "LAPICERO", "USB", "BOLSO", "CARGADOR"],
        "preferred_categories": ["Oficina", "Termos", "Escritura", "Tecnologia"],
        "preferred_materials": ["METAL", "ACERO_INOXIDABLE", "MADERA", "VIDRIO"],
        "preferred_attributes": ["PREMIUM", "ELEGANTE", "MODERNO", "EJECUTIVO"],
        "avoid_families": ["LLAVERO", "GORRA"],
        "avoid_categories": ["Juguetes"],
        "use_cases": ["VISITAS_OBRA", "CONVENCIÓN", "LANZAMIENTO", "CLIENTES"],
    },
    "INGENIEROS": {
        "preferred_families": ["BOTELLA", "TERMO", "USB", "CARGADOR", "CALCULADORA", "LINterna", "MOUSE"],
        "preferred_categories": ["Tecnologia", "Oficina", "Herramientas", "Termos"],
        "preferred_materials": ["METAL", "ALUMINIO", "PLASTICO", "NEOPRENO"],
        "preferred_attributes": ["RESISTENTE", "PORTATIL", "COMPACTO", "LIGERO"],
        "avoid_families": ["PULSERA", "MONEDERO", "NECESER"],
        "avoid_categories": ["Belleza", "Moda"],
        "use_cases": ["OBRA", "CAPACITACION", "FERIAS", "EVENTOS_TECNICOS"],
    },
    "ABOGADOS": {
        "preferred_families": ["AGENDA", "LAPICERO", "PORTAFOLIO", "BOLSO", "CALCULADORA", "TARJETERO", "PARAGUAS"],
        "preferred_categories": ["Oficina", "Escritura", "Bolsos", "Accesorios"],
        "preferred_materials": ["CUERO", "METAL", "MADERA"],
        "preferred_attributes": ["EJECUTIVO", "PREMIUM", "ELEGANTE", "PROFESIONAL", "CLASICO"],
        "avoid_families": ["GORRA", "TOALLA", "ROPA", "PULSERA"],
        "avoid_categories": ["Deportes", "Juguetes"],
        "use_cases": ["REUNIONES", "CONFERENCIAS", "CLIENTES", "CONGRESOS"],
    },
    "PROFESORES": {
        "preferred_families": ["AGENDA", "LAPICERO", "LIBRETA", "USB", "BOTELLA", "TERMO", "BOLSO"],
        "preferred_categories": ["Escritura", "Libretas", "Oficina", "Eco", "Termos"],
        "preferred_materials": ["RPET", "BAMBU", "CORCHO", "ALGODON"],
        "preferred_attributes": ["REUTILIZABLE", "ECOLOGICO", "LIGERO"],
        "avoid_families": ["PULSERA", "GAFAS"],
        "avoid_categories": ["Juguetes", "Belleza"],
        "use_cases": ["CAPACITACION", "WORKSHOP", "CLASES", "CONFERENCIAS"],
    },
    "ESTUDIANTES": {
        "preferred_families": ["LIBRETA", "LAPICERO", "MOCHILA", "USB", "CALCULADORA", "BOTELLA", "LONCHERA"],
        "preferred_categories": ["Escritura", "Libretas", "Escolar", "Tecnologia"],
        "preferred_materials": ["PLASTICO", "RPET", "ALGODON"],
        "preferred_attributes": ["LIGERO", "PORTATIL", "COMPACTO", "RECARGABLE"],
        "avoid_families": ["RELOJ", "CARTERA", "PARAGUAS"],
        "avoid_categories": ["Hogar", "Herramientas"],
        "use_cases": ["UNIVERSIDAD", "ESTUDIO", "EXAMENES"],
    },
    "UNIVERSITARIOS": {
        "preferred_families": ["MOCHILA", "LIBRETA", "LAPICERO", "USB", "BOTELLA", "CARGADOR", "CALCULADORA"],
        "preferred_categories": ["Escritura", "Libretas", "Escolar", "Tecnologia", "Bolsos"],
        "preferred_materials": ["RPET", "PLASTICO", "METAL"],
        "preferred_attributes": ["RECARGABLE", "PORTATIL", "MODERNO"],
        "avoid_families": ["RELOJ", "PULSERA", "GAFAS"],
        "avoid_categories": ["Hogar"],
        "use_cases": ["UNIVERSIDAD", "ESTUDIO", "GRADUACION", "EVENTOS"],
    },
    "EMPRESA": {
        "preferred_families": ["USB", "AGENDA", "LAPICERO", "BOTELLA", "TERMO", "BOLSO", "CARGADOR", "MUG"],
        "preferred_categories": ["Oficina", "Tecnologia", "Escritura", "Termos", "Bolsos"],
        "preferred_materials": ["METAL", "PLASTICO", "RPET", "VIDRIO"],
        "preferred_attributes": ["CORPORATIVO", "PERSONALIZABLE", "PREMIUM", "PROFESIONAL"],
        "avoid_families": ["PULSERA", "GORRA", "TOALLA"],
        "avoid_categories": ["Juguetes"],
        "use_cases": ["EVENTOS_CORPORATIVOS", "BIENVENIDA", "CAPACITACION", "FERIAS"],
    },
    "OFICINA": {
        "preferred_families": ["AGENDA", "LAPICERO", "BOTELLA", "MUG", "USB", "CALCULADORA", "ORGANIZADOR"],
        "preferred_categories": ["Oficina", "Escritura", "Libretas", "Termos"],
        "preferred_materials": ["METAL", "PLASTICO", "MADERA"],
        "preferred_attributes": ["CORPORATIVO", "PRACTICO", "FUNCIONAL"],
        "avoid_families": ["MOCHILA", "NEVERA", "TOALLA"],
        "avoid_categories": ["Deportes", "Belleza"],
        "use_cases": ["OFICINA", "REUNIONES", "DIA_TRABAJO"],
    },
    "CONSTRUCTORAS": {
        "preferred_families": ["BOTELLA", "TERMO", "NEVERA", "LINterna", "MOCHILA", "CARGADOR", "TOALLA"],
        "preferred_categories": ["Termos", "Herramientas", "Bolsos"],
        "preferred_materials": ["METAL", "ACERO_INOXIDABLE", "NEOPRENO", "PLASTICO"],
        "preferred_attributes": ["RESISTENTE", "IMPERMEABLE", "PORTATIL", "DURADERO"],
        "avoid_families": ["PULSERA", "PORTAFOLIO", "TARJETERO"],
        "avoid_categories": ["Belleza", "Moda", "Ceramica", "Vidrio"],
        "use_cases": ["OBRA", "CAPACITACION", "BIENVENIDA", "EVENTOS_CONSTRUCCION"],
    },
    "BANCOS": {
        "preferred_families": ["AGENDA", "LAPICERO", "USB", "CALCULADORA", "PORTAFOLIO", "PARAGUAS", "RELOJ"],
        "preferred_categories": ["Oficina", "Escritura", "Tecnologia", "Accesorios"],
        "preferred_materials": ["CUERO", "METAL", "VIDRIO", "MADERA"],
        "preferred_attributes": ["EJECUTIVO", "PREMIUM", "PROFESIONAL", "ELEGANTE"],
        "avoid_families": ["GORRA", "MOCHILA", "PULSERA", "TOALLA"],
        "avoid_categories": ["Deportes", "Juguetes"],
        "use_cases": ["CLIENTES", "EJECUTIVOS", "EVENTOS_FINANCIEROS", "CIERRE_ANUAL"],
    },
    "EVENTOS": {
        "preferred_families": ["USB", "LLAVERO", "GORRA", "BOLSO", "MUG", "BOTELLA", "CARGADOR"],
        "preferred_categories": ["Accesorios", "Tecnologia", "Bolsos", "Termos"],
        "preferred_materials": ["PLASTICO", "RPET", "ALGODON", "METAL"],
        "preferred_attributes": ["PERSONALIZABLE", "LIGERO", "PROMOCIONAL"],
        "avoid_families": ["RELOJ", "TARJETERO", "PORTAFOLIO"],
        "avoid_categories": ["Hogar"],
        "use_cases": ["FERIAS", "CONGRESOS", "CONVENCIONES", "LANZAMIENTOS"],
    },
    "VIP": {
        "preferred_families": ["RELOJ", "BOLSO", "TERMO", "PORTAFOLIO", "MALETA", "LAPICERO", "AGENDA", "CARGADOR"],
        "preferred_categories": ["Accesorios", "Bolsos", "Termos", "Oficina"],
        "preferred_materials": ["CUERO", "METAL", "VIDRIO", "ACERO_INOXIDABLE", "MADERA"],
        "preferred_attributes": ["PREMIUM", "LUJO", "EXCLUSIVO", "ELEGANTE", "EJECUTIVO"],
        "avoid_families": ["LLAVERO", "GORRA", "PULSERA"],
        "avoid_categories": ["Escolar", "Juguetes", "Promocional"],
        "use_cases": ["RECONOCIMIENTO", "PREMIOS", "CIERRE_ANUAL", "CLIENTES_VIP"],
    },
    "FERIAS": {
        "preferred_families": ["USB", "LLAVERO", "GORRA", "BOLSO", "MUG", "BOTELLA", "CARGADOR", "LAPICERO"],
        "preferred_categories": ["Accesorios", "Tecnologia", "Bolsos", "Escritura"],
        "preferred_materials": ["PLASTICO", "RPET", "ALGODON", "METAL"],
        "preferred_attributes": ["PERSONALIZABLE", "LIGERO", "PROMOCIONAL", "ECONOMICO"],
        "avoid_families": ["RELOJ", "TARJETERO", "PORTAFOLIO", "MALETA"],
        "avoid_categories": ["Hogar", "Belleza"],
        "use_cases": ["FERIAS_COMERCIALES", "EXPOSICIONES", "STAND", "CAPTACION_CLIENTES"],
    },
    "LANZAMIENTO": {
        "preferred_families": ["USB", "CARGADOR", "AUDIFONOS", "BOLSO", "MUG", "BOTELLA", "GORRA"],
        "preferred_categories": ["Tecnologia", "Accesorios", "Bolsos", "Termos"],
        "preferred_materials": ["METAL", "PLASTICO", "RPET", "ALUMINIO"],
        "preferred_attributes": ["MODERNO", "INOVADOR", "PERSONALIZABLE", "LLAMATIVO"],
        "avoid_families": ["TARJETERO", "CALCULADORA", "PARAGUAS"],
        "avoid_categories": ["Hogar", "Juguetes"],
        "use_cases": ["LANZAMIENTO_PRODUCTO", "INVITADOS", "MEDIOS", "EVENTO_LANZAMIENTO"],
    },
    "BIENVENIDA": {
        "preferred_families": ["BOTELLA", "TERMO", "MUG", "AGENDA", "LAPICERO", "BOLSO", "USB", "MOCHILA"],
        "preferred_categories": ["Termos", "Oficina", "Escritura", "Bolsos"],
        "preferred_materials": ["RPET", "METAL", "PLASTICO", "BAMBU"],
        "preferred_attributes": ["CORPORATIVO", "PRACTICO", "REUTILIZABLE"],
        "avoid_families": ["PULSERA", "GAFAS", "ROPA"],
        "avoid_categories": ["Belleza"],
        "use_cases": ["ONBOARDING", "NUEVOS_EMPLEADOS", "KIT_BIENVENIDA"],
    },
}

CATEGORY_RECOMMENDATIONS: dict[str, dict] = {
    "Tecnologia": {
        "preferred_families": ["USB", "CARGADOR", "AUDIFONOS", "MOUSE", "HUB", "CABLE"],
        "preferred_technologies": ["BLUETOOTH", "WIRELESS", "USB_C", "QI", "RFID"],
        "preferred_attributes": ["INOVADOR", "MODERNO", "DIGITAL"],
        "use_cases": ["EVENTOS_TECNOLOGIA", "LANZAMIENTO", "FERIAS_TECH"],
    },
    "Eco": {
        "preferred_families": ["BOTELLA", "BOLSO", "LIBRETA", "LAPICERO", "USB"],
        "preferred_materials": ["RPET", "BAMBU", "CORCHO", "ALGODON", "RECICLADO"],
        "preferred_attributes": ["ECOLOGICO", "SOSTENIBLE", "REUTILIZABLE", "NATURAL"],
        "use_cases": ["CAMPAÑAS_ECO", "SOSTENIBILIDAD", "CONCIENCIA_AMBIENTAL"],
    },
    "Oficina": {
        "preferred_families": ["AGENDA", "LAPICERO", "CALCULADORA", "USB", "ORGANIZADOR"],
        "preferred_attributes": ["CORPORATIVO", "PROFESIONAL", "EJECUTIVO"],
        "preferred_materials": ["METAL", "MADERA", "CUERO"],
        "use_cases": ["OFICINA", "REUNIONES", "TRABAJO_DIARIO"],
    },
    "Deportes": {
        "preferred_families": ["BOTELLA", "TOALLA", "GORRA", "MOCHILA", "PULSERA"],
        "preferred_attributes": ["RESISTENTE", "LIGERO", "PORTATIL", "IMPERMEABLE"],
        "preferred_materials": ["NEOPRENO", "ALGODON", "SILICONA"],
        "use_cases": ["EVENTOS_DEPORTIVOS", "GIMNASIO", "COMPETENCIAS"],
    },
    "Termos": {
        "preferred_families": ["BOTELLA", "TERMO", "MUG"],
        "preferred_attributes": ["TERMICO", "AISLANTE", "RESISTENTE"],
        "preferred_materials": ["ACERO_INOXIDABLE", "METAL", "VIDRIO"],
        "use_cases": ["HIDRATACION", "OFICINA", "VIAJES"],
    },
    "Escritura": {
        "preferred_families": ["LAPICERO", "AGENDA", "LIBRETA", "CALCULADORA"],
        "preferred_attributes": ["PROFESIONAL", "EJECUTIVO", "CLASICO"],
        "preferred_materials": ["METAL", "MADERA", "PLASTICO"],
        "use_cases": ["OFICINA", "CAPACITACION", "UNIVERSIDAD"],
    },
    "Salud": {
        "preferred_families": ["BOTELLA", "TERMO", "TOALLA", "BOLSO", "USB"],
        "preferred_attributes": ["IMPERMEABLE", "RESISTENTE", "ANTIBACTERIAL"],
        "preferred_materials": ["METAL", "BAMBU", "RPET", "ALGODON"],
        "use_cases": ["JORNADAS_SALUD", "CONGRESOS_MEDICOS", "CAMPAÑAS"],
    },
}

TECHNOLOGY_RECOMMENDATIONS: dict[str, dict] = {
    "BLUETOOTH": {
        "preferred_families": ["AUDIFONOS", "SPEAKER", "MOUSE", "TECLADO"],
        "preferred_attributes": ["WIRELESS", "INALAMBRICO", "MODERNO"],
        "use_cases": ["TECNOLOGIA", "OFICINA", "MOVILIDAD"],
    },
    "WIRELESS": {
        "preferred_families": ["MOUSE", "TECLADO", "AUDIFONOS", "CARGADOR"],
        "preferred_attributes": ["_PORTATIL", "MODERNO", "SIN_CABLES"],
        "use_cases": ["OFICINA", "MOVILIDAD", "TECNOLOGIA"],
    },
    "USB_C": {
        "preferred_families": ["CABLE", "HUB", "CARGADOR", "USB"],
        "preferred_attributes": ["MODERNO", "RAPIDO", "VERSATIL"],
        "use_cases": ["TECNOLOGIA", "ACTUALIZACION"],
    },
    "RFID": {
        "preferred_families": ["BILLETERA", "TARJETERO", "PORTAFOLIO"],
        "preferred_attributes": ["SEGURIDAD", "TECNOLOGICO"],
        "use_cases": ["SEGURIDAD", "PROTECCION_DATOS"],
    },
    "QI": {
        "preferred_families": ["CARGADOR"],
        "preferred_attributes": ["INALAMBRICO", "MODERNO"],
        "use_cases": ["TECNOLOGIA", "OFICINA"],
    },
}

PRICE_INTENT_RECOMMENDATIONS: dict[str, dict] = {
    "LOW_PRICE": {
        "preferred_families": ["LAPICERO", "LLAVERO", "USB", "GORRA", "MUG", "BOLSO"],
        "preferred_materials": ["PLASTICO", "ALGODON", "RPET"],
        "preferred_attributes": ["ECONOMICO", "PROMOCIONAL", "LIGERO"],
        "use_cases": ["MASIVO", "PROMOCION", "FERIA"],
    },
    "HIGH_PRICE": {
        "preferred_families": ["RELOJ", "TERMO", "BOLSO", "PORTAFOLIO", "MALETA", "LAPICERO"],
        "preferred_materials": ["CUERO", "METAL", "ACERO_INOXIDABLE", "VIDRIO", "MADERA"],
        "preferred_attributes": ["PREMIUM", "LUJO", "EXCLUSIVO", "ELEGANTE", "EJECUTIVO"],
        "use_cases": ["RECONOCIMIENTO", "PREMIOS", "CLIENTES_VIP", "CIERRE_ANUAL"],
    },
}

QUALITY_RECOMMENDATIONS: dict[str, dict] = {
    "HIGH_QUALITY": {
        "preferred_families": ["RELOJ", "TERMO", "BOLSO", "PORTAFOLIO", "LAPICERO", "AGENDA", "MALETA"],
        "preferred_materials": ["CUERO", "METAL", "ACERO_INOXIDABLE", "VIDRIO", "MADERA"],
        "preferred_attributes": ["PREMIUM", "EJECUTIVO", "ELEGANTE", "PROFESIONAL"],
        "use_cases": ["RECONOCIMIENTO", "CLIENTES_VIP", "EJECUTIVOS"],
    },
}


def get_audience_rules(audience: str) -> Optional[dict]:
    return AUDIENCE_RECOMMENDATIONS.get(audience)


def get_category_rules(category: str) -> Optional[dict]:
    for key, rules in CATEGORY_RECOMMENDATIONS.items():
        if key.lower() == category.lower():
            return rules
    return None


def get_technology_rules(tech: str) -> Optional[dict]:
    return TECHNOLOGY_RECOMMENDATIONS.get(tech)


def get_price_rules(price_intent: str) -> Optional[dict]:
    return PRICE_INTENT_RECOMMENDATIONS.get(price_intent)


def get_quality_rules(quality_intent: str) -> Optional[dict]:
    return QUALITY_RECOMMENDATIONS.get(quality_intent)
