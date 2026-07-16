from typing import Dict, List, Optional, Set


class IndustryProfile:
    """Perfil comercial configurable de una industria.

    `prefer`/`avoid`/`context_tags` se mantienen por compatibilidad.
    La afinidad comercial determinista se define con:
    - preferred_categories / preferred_tags / preferred_materials
    - preferred_roles
    - blacklisted_categories / blacklisted_tags
    Todo es configurable vía DEFAULT_PROFILES.
    """

    def __init__(
        self,
        industry: str,
        prefer: List[str],
        avoid: List[str],
        context_tags: List[str] = None,
        preferred_categories: List[str] = None,
        preferred_tags: List[str] = None,
        preferred_materials: List[str] = None,
        preferred_roles: List[str] = None,
        blacklisted_categories: List[str] = None,
        blacklisted_tags: List[str] = None,
    ) -> None:
        self.industry = industry
        self.prefer: Set[str] = {s.lower() for s in prefer}
        self.avoid: Set[str] = {s.lower() for s in avoid}
        self.context_tags: Set[str] = {s.lower() for s in (context_tags or [])}
        self.preferred_categories: Set[str] = {s.lower() for s in (preferred_categories or [])}
        self.preferred_tags: Set[str] = {s.lower() for s in (preferred_tags or [])}
        self.preferred_materials: Set[str] = {s.lower() for s in (preferred_materials or [])}
        self.preferred_roles: Set[str] = {s.lower() for s in (preferred_roles or [])}
        self.blacklisted_categories: Set[str] = {s.lower() for s in (blacklisted_categories or [])}
        self.blacklisted_tags: Set[str] = {s.lower() for s in (blacklisted_tags or [])}


# Perfiles por defecto. Completamente configurables.
DEFAULT_PROFILES: Dict[str, IndustryProfile] = {
    "arquitectura": IndustryProfile(
        "arquitectura",
        prefer=[
            "escritorio", "organizacion", "organización", "oficina", "madera",
            "bambu", "bambú", "diseno", "diseño", "premium", "ejecutivo",
            "planos", "construccion", "construcción", "libreta", "agenda",
            "boligrafo", "bolígrafo", "laptop", "croquis", "maqueta",
        ],
        avoid=[
            "mascotas", "mascota", "correa", "bowl", "juguete", "infantil",
            "niños", "ninos", "cocina", "bebe", "bebé", "animal",
        ],
        context_tags=["oficina", "escritorio", "diseno", "diseño", "planos", "construccion", "construcción"],
        preferred_categories=["oficina", "escritura", "bolsos", "viaje", "tecnologia"],
        preferred_tags=["premium", "ejecutivo", "personalizable", "organizacion", "libreta", "agenda", "maleta"],
        preferred_materials=["cuero", "madera", "bambu", "metal", "aluminio"],
        preferred_roles=["CORE", "UTILITY"],
        blacklisted_categories=["mascotas", "juguetes", "cocina", "bebe"],
        blacklisted_tags=["juguete", "infantil", "mascota", "cocina"],
    ),
    "construccion": IndustryProfile(
        "construccion",
        prefer=[
            "obra", "seguridad", "herramienta", "casco", "construccion",
            "construcción", "oficina", "chaleco", "alarma", "linterna",
            "organizacion", "organización", "durabilidad",
        ],
        avoid=["mascotas", "mascota", "juguete", "infantil", "cocina", "bebe", "bebé"],
        context_tags=["obra", "seguridad", "herramienta", "construccion", "construcción"],
        preferred_categories=["oficina", "viaje", "tecnologia", "hogar"],
        preferred_tags=["utilidad", "durabilidad", "seguridad", "herramienta"],
        preferred_materials=["metal", "aluminio", "acero", "plastico"],
        preferred_roles=["CORE", "UTILITY"],
        blacklisted_categories=["mascotas", "juguetes", "cocina", "bebe"],
        blacklisted_tags=["juguete", "infantil", "mascota", "cocina"],
    ),
    "ingenieria": IndustryProfile(
        "ingenieria",
        prefer=[
            "oficina", "tecnicos", "técnicos", "ingenieria", "ingeniería",
            "escritorio", "organizacion", "organización", "calculadora",
            "libreta", "boligrafo", "bolígrafo", "precision",
        ],
        avoid=["mascotas", "mascota", "juguete", "infantil", "cocina"],
        context_tags=["oficina", "tecnicos", "técnicos", "ingenieria", "ingeniería"],
        preferred_categories=["oficina", "escritura", "tecnologia", "bolsos"],
        preferred_tags=["tecnicos", "utilidad", "precision", "calculadora", "libreta"],
        preferred_materials=["metal", "plastico", "aluminio"],
        preferred_roles=["CORE", "UTILITY"],
        blacklisted_categories=["mascotas", "juguetes", "cocina"],
        blacklisted_tags=["juguete", "infantil", "mascota", "cocina"],
    ),
    "tecnologia": IndustryProfile(
        "tecnologia",
        prefer=[
            "usb", "cargador", "gadget", "wireless", "mouse", "oficina",
            "tecnologia", "tecnología", "auricular", "power bank", "cable",
            "electronica", "electrónica", "innovacion", "innovación",
        ],
        avoid=["mascotas", "mascota", "juguete", "cocina", "infantil"],
        context_tags=["tecnologia", "tecnología", "oficina", "gadget", "branding"],
        preferred_categories=["tecnologia", "escritura", "oficina", "hogar"],
        preferred_tags=["usb", "cargador", "gadget", "wireless", "auricular", "power bank", "tecnicos"],
        preferred_materials=["plastico", "metal", "silicona", "aluminio"],
        preferred_roles=["CORE", "UTILITY", "PROMOTIONAL"],
        blacklisted_categories=["mascotas", "juguetes", "cocina"],
        blacklisted_tags=["juguete", "infantil", "mascota", "cocina"],
    ),
    "software": IndustryProfile(
        "software",
        prefer=[
            "usb", "cargador", "gadget", "wireless", "mouse", "oficina",
            "tecnologia", "tecnología", "auricular", "power bank", "cable",
            "electronica", "electrónica", "innovacion", "innovación",
        ],
        avoid=["mascotas", "mascota", "juguete", "cocina", "infantil"],
        context_tags=["tecnologia", "tecnología", "oficina", "gadget", "branding"],
        preferred_categories=["tecnologia", "escritura", "oficina", "hogar", "bolsos"],
        preferred_tags=["usb", "cargador", "gadget", "wireless", "auricular", "power bank", "tecnicos", "mouse pad", "hub"],
        preferred_materials=["plastico", "metal", "silicona", "aluminio"],
        preferred_roles=["CORE", "UTILITY", "PROMOTIONAL"],
        blacklisted_categories=["mascotas", "juguetes", "cocina", "salud", "higiene"],
        blacklisted_tags=["cepillo", "pastillero", "borrador", "escolar", "utiles escolares", "poncho", "higiene", "salud"],
    ),
    "salud": IndustryProfile(
        "salud",
        prefer=[
            "termos", "termo", "escritorio", "libretas", "organizacion",
            "organización", "bienestar", "salud", "agenda", "mochila",
            "botella", "hidratacion", "hidratación", "clinica", "clínica",
        ],
        avoid=["mascotas", "mascota", "juguete", "infantil", "cocina"],
        context_tags=["termos", "escritorio", "libretas", "organizacion", "organización", "bienestar"],
        preferred_categories=["hogar", "oficina", "bolsos", "viaje"],
        preferred_tags=["bienestar", "salud", "hidratacion", "botella", "termo", "higiene"],
        preferred_materials=["acero", "bambu", "aluminio", "plastico"],
        preferred_roles=["CORE", "UTILITY"],
        blacklisted_categories=["mascotas", "juguetes", "cocina", "escritura escolar"],
        blacklisted_tags=["juguete", "infantil", "mascota", "cocina", "escolar"],
    ),
    "hospital": IndustryProfile(
        "hospital",
        prefer=[
            "termos", "termo", "escritorio", "libretas", "organizacion",
            "organización", "bienestar", "salud", "agenda", "botella",
            "clinica", "clínica", "mochila", "hidratacion", "hidratación",
        ],
        avoid=["mascotas", "mascota", "juguete", "infantil", "cocina"],
        context_tags=["salud", "medicos", "médicos", "bienestar", "oficina"],
        preferred_categories=["hogar", "oficina", "bolsos", "viaje"],
        preferred_tags=["bienestar", "salud", "hidratacion", "botella", "termo", "higiene"],
        preferred_materials=["acero", "bambu", "aluminio", "plastico"],
        preferred_roles=["CORE", "UTILITY"],
        blacklisted_categories=["mascotas", "juguetes", "cocina", "escritura escolar"],
        blacklisted_tags=["juguete", "infantil", "mascota", "cocina", "escolar"],
    ),
    "clinica": IndustryProfile(
        "clinica",
        prefer=[
            "termos", "termo", "escritorio", "libretas", "organizacion",
            "organización", "bienestar", "salud", "agenda", "botella",
            "clinica", "clínica", "mochila", "hidratacion", "hidratación",
        ],
        avoid=["mascotas", "mascota", "juguete", "infantil", "cocina"],
        context_tags=["salud", "medicos", "médicos", "bienestar", "oficina"],
        preferred_categories=["hogar", "oficina", "bolsos", "viaje"],
        preferred_tags=["bienestar", "salud", "hidratacion", "botella", "termo", "higiene"],
        preferred_materials=["acero", "bambu", "aluminio", "plastico"],
        preferred_roles=["CORE", "UTILITY"],
        blacklisted_categories=["mascotas", "juguetes", "cocina", "escritura escolar"],
        blacklisted_tags=["juguete", "infantil", "mascota", "cocina", "escolar"],
    ),
    "educacion": IndustryProfile(
        "educacion",
        prefer=[
            "cuadernos", "libretas", "esferos", "mochilas", "termos",
            "cuaderno", "agenda", "boligrafo", "bolígrafo", "estuche",
            "estudiante", "escuela", "universidad", "lapices", "lápices",
        ],
        avoid=["mascotas", "mascota", "alcohol", "cocina"],
        context_tags=["estudiantes", "educacion", "educación", "oficina", "merchandising"],
        preferred_categories=["oficina", "escritura", "bolsos"],
        preferred_tags=["cuaderno", "libreta", "estudiante", "escuela", "mochila", "lapices"],
        preferred_materials=["papel", "carton", "plastico", "metal"],
        preferred_roles=["CORE", "UTILITY"],
        blacklisted_categories=["mascotas", "alcohol", "cocina"],
        blacklisted_tags=["mascota", "alcohol", "cocina"],
    ),
    "universidad": IndustryProfile(
        "universidad",
        prefer=[
            "cuadernos", "libretas", "mochilas", "termos", "cuaderno", "agenda",
            "boligrafo", "bolígrafo", "estuche", "estudiante", "campus",
            "merchandising", "lid", "gorra",
        ],
        avoid=["mascotas", "mascota", "alcohol"],
        context_tags=["estudiantes", "educacion", "educación", "oficina", "merchandising"],
        preferred_categories=["oficina", "escritura", "bolsos"],
        preferred_tags=["cuaderno", "libreta", "estudiante", "campus", "mochila", "gorra"],
        preferred_materials=["papel", "carton", "plastico", "metal"],
        preferred_roles=["CORE", "UTILITY", "PROMOTIONAL"],
        blacklisted_categories=["mascotas", "alcohol"],
        blacklisted_tags=["mascota", "alcohol"],
    ),
    "colegio": IndustryProfile(
        "colegio",
        prefer=[
            "cuadernos", "libretas", "mochilas", "cuaderno", "agenda",
            "boligrafo", "bolígrafo", "estuche", "estudiante", "infantil",
            "colorido", "didactico", "didáctico", "lapices", "lápices",
        ],
        avoid=["mascotas", "mascota", "alcohol"],
        context_tags=["estudiantes", "educacion", "educación", "infantil", "merchandising"],
        preferred_categories=["oficina", "escritura", "bolsos"],
        preferred_tags=["cuaderno", "libreta", "estudiante", "infantil", "colorido", "didactico"],
        preferred_materials=["papel", "carton", "plastico", "madera"],
        preferred_roles=["CORE", "UTILITY"],
        blacklisted_categories=["mascotas", "alcohol"],
        blacklisted_tags=["mascota", "alcohol"],
    ),
    "finanzas": IndustryProfile(
        "finanzas",
        prefer=[
            "ejecutivo", "corporativo", "oficina", "branding", "alta gama",
            "lujo", "agenda", "libreta", "tarjeta", "premium", "escritorio",
            "organizacion", "organización", "boligrafo", "bolígrafo",
        ],
        avoid=["mascotas", "mascota", "juguete", "infantil", "cocina"],
        context_tags=["corporativo", "ejecutivo", "oficina", "branding", "alta gama"],
        preferred_categories=["oficina", "escritura", "viaje", "tecnologia"],
        preferred_tags=["ejecutivo", "premium", "corporativo", "alta gama", "agenda", "libreta", "tarjeta"],
        preferred_materials=["cuero", "metal", "madera", "aluminio"],
        preferred_roles=["CORE", "UTILITY", "PREMIUM"],
        blacklisted_categories=["mascotas", "juguetes", "cocina"],
        blacklisted_tags=["juguete", "infantil", "mascota", "cocina"],
    ),
    "hoteleria": IndustryProfile(
        "hoteleria",
        prefer=[
            "hotel", "hospedaje", "amenities", "bienvenida", "toalla", "kit",
            "viaje", "maleta", "colonia", "aroma", "recepcion", "recepción",
            "bienestar", "regalo",
        ],
        avoid=["mascotas", "mascota", "juguete", "infantil"],
        context_tags=["hotel", "hospedaje", "bienvenida", "viaje", "bienestar"],
        preferred_categories=["hogar", "viaje", "otros"],
        preferred_tags=["hotel", "amenities", "bienvenida", "kit", "viaje", "maleta"],
        preferred_materials=["algodon", "plastico", "vidrio", "metal"],
        preferred_roles=["CORE", "UTILITY"],
        blacklisted_categories=["mascotas", "juguetes"],
        blacklisted_tags=["juguete", "infantil", "mascota"],
    ),
    "vip": IndustryProfile(
        "vip",
        prefer=[
            "premium", "lujo", "ejecutivo", "alta gama", "exclusivo",
            "cuero", "metal", "madera", "bambu", "bambú", "edicion", "edición",
            "limitada", "detalle",
        ],
        avoid=["mascotas", "mascota", "juguete", "infantil", "plástico", "plastico"],
        context_tags=["premium", "lujo", "ejecutivo", "alta gama"],
        preferred_categories=["viaje", "oficina", "escritura", "tecnologia"],
        preferred_tags=["premium", "lujo", "exclusivo", "alta gama", "cuero", "metal", "madera"],
        preferred_materials=["cuero", "metal", "madera", "bambu", "aluminio", "vidrio"],
        preferred_roles=["CORE", "PREMIUM", "UTILITY"],
        blacklisted_categories=["mascotas", "juguetes", "plastico"],
        blacklisted_tags=["juguete", "infantil", "mascota", "plastico"],
    ),
    "eventos": IndustryProfile(
        "eventos",
        prefer=[
            "evento", "feria", "congreso", "stand", "merchandising", "branding",
            "logo", "regalo", "welcome", "bienvenida", "bolsa", "mochila",
        ],
        avoid=["mascotas", "mascota", "cocina"],
        context_tags=["evento", "feria", "congreso", "merchandising", "stand"],
        preferred_categories=["otros", "bolsos", "oficina", "escritura"],
        preferred_tags=["evento", "merchandising", "branding", "logo", "welcome", "bolsa"],
        preferred_materials=["plastico", "carton", "algodon", "metal"],
        preferred_roles=["CORE", "PROMOTIONAL", "ACCESSORY"],
        blacklisted_categories=["mascotas", "cocina"],
        blacklisted_tags=["mascota", "cocina"],
    ),
}


class IndustryKnowledge:
    def __init__(self, profiles: Dict[str, IndustryProfile] = None) -> None:
        self.profiles = profiles or DEFAULT_PROFILES

    def get(self, industry: Optional[str]) -> Optional[IndustryProfile]:
        if not industry:
            return None
        profile = self.profiles.get(industry)
        if profile is not None:
            return profile
        # Sinonimos: la clave de intencion puede no coincidir literalmente
        # con la clave del perfil (ej. 'financiera' -> 'finanzas').
        synonyms = {
            "financiera": "finanzas",
            "finanzas": "financiera",
            "salud": "hospital",
            "clinica": "hospital",
            "educacion": "colegio",
        }
        alt = synonyms.get(industry)
        if alt:
            return self.profiles.get(alt)
        return None

    def industry_for(self, text: str) -> Optional[str]:
        from ...application.intent_analyzer import INDUSTRIES

        normalized = " ".join(text.lower().split())
        for canonical, variants in INDUSTRIES.items():
            if any(v in normalized for v in variants):
                return canonical
        return None

    def industry_score(self, industry: str, product_signals: str) -> float:
        """Score 0..1 del producto frente a la industria.

        - 1.0 si coincide con `prefer`.
        - 0.0 si coincide con `avoid` (penalizacion fuerte).
        - 0.5 neutral.
        """
        profile = self.get(industry)
        if profile is None:
            return 0.5
        text = product_signals.lower()
        if any(a in text for a in profile.avoid):
            return 0.0
        if any(p in text for p in profile.prefer):
            return 1.0
        return 0.5

    def is_avoided(self, industry: str, product_signals: str) -> bool:
        profile = self.get(industry)
        if profile is None:
            return False
        text = product_signals.lower()
        return any(a in text for a in profile.avoid)
