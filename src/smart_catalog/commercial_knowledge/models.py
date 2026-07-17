from dataclasses import dataclass, field


@dataclass
class CommercialKnowledge:
    product_reference: str = ""
    product_family: str = ""
    commercial_categories: list[str] = field(default_factory=list)
    industry_affinity: list[str] = field(default_factory=list)
    customer_profiles: list[str] = field(default_factory=list)
    executive_level: str = "low"
    premium_level: str = "basic"
    commercial_value: str = "economic"
    gift_occasions: list[str] = field(default_factory=list)
    recommended_campaigns: list[str] = field(default_factory=list)
    use_cases: list[str] = field(default_factory=list)
    corporate_affinity: float = 0.0
    perceived_value: str = "estandar"
    commercial_tags: list[str] = field(default_factory=list)
    search_boost_tags: list[str] = field(default_factory=list)
    search_penalty_tags: list[str] = field(default_factory=list)
    confidence: float = 0.0
    reason: str = ""


AUDIENCE_TO_INDUSTRY: dict[str, str] = {
    "MEDICOS": "SALUD",
    "ARQUITECTOS": "ARQUITECTURA",
    "INGENIEROS": "INGENIERIA",
    "ABOGADOS": "LEGAL",
    "PROFESORES": "EDUCACION",
    "UNIVERSITARIOS": "EDUCACION",
    "ESTUDIANTES": "EDUCACION",
    "EMPRESA": "CORPORATIVO",
    "OFICINA": "OFICINA",
    "EVENTOS": "EVENTOS",
    "FERIAS": "EVENTOS",
    "NINOS": "EDUCACION",
}

INDUSTRY_SYNONYMS: dict[str, list[str]] = {
    "ARQUITECTURA": ["arquitectura", "arquitectos", "constructora", "construccion"],
    "INGENIERIA": ["ingenieria", "ingenieros", "construccion", "civil"],
    "CONSTRUCCION": ["construccion", "constructora", "obra", "edificacion"],
    "TECNOLOGIA": ["tecnologia", "tecnologico", "tech", "startup", "startups", "informatica"],
    "SALUD": ["salud", "medico", "medicos", "hospital", "clinica", "enfermeria"],
    "EDUCACION": ["educacion", "colegio", "universidad", "universitario", "escuela", "profesor", "docente"],
    "FINANCIERO": ["banco", "bancario", "financiero", "seguros", "inversion"],
    "CONSULTORIA": ["consultoria", "consultor", "consultora", "asesoria"],
    "LEGAL": ["legal", "abogado", "abogados", "bufete", "juridico"],
    "CORPORATIVO": ["corporativo", "corporacion", "empresa", "empresarial"],
    "TELECOMUNICACIONES": ["telecomunicaciones", "telefonia", "comunicaciones"],
    "OUTDOOR": ["outdoor", "campo", "naturaleza", "aire libre"],
    "DEPORTES": ["deportes", "deportivo", "gimnasio", "fitness"],
    "EVENTOS": ["eventos", "feria", "convencion", "congreso", "conferencia"],
    "VIAJES": ["viajes", "turismo", "hoteleria", "hotel"],
    "MODA": ["moda", "vestuario", "textil"],
}

PROFILE_SYNONYMS: dict[str, list[str]] = {
    "EJECUTIVO": ["ejecutivo", "ejecutiva", "gerente", "directivo", "ceo", "director"],
    "VIP": ["vip", "cliente_vip", "cliente especial", "premium", "exclusivo"],
    "COMERCIAL": ["comercial", "ventas", "vendedor", "representante"],
    "ADMINISTRATIVO": ["administrativo", "asistente", "oficina", "secretaria"],
    "PROFESIONAL": ["profesional", "especialista", "consultor", "analista"],
    "TECNOLOGICO": ["tecnologico", "developer", "programador", "sistemas", "it"],
    "DEPORTISTA": ["deportista", "atleta", "fitness", "entrenador"],
    "VIAJERO": ["viajero", "frecuente", "ejecutivo viaje"],
}
