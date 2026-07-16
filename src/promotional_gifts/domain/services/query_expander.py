from typing import Dict, List

SYNONYM_MAP: Dict[str, List[str]] = {
    "maleta ejecutiva": ["backpack", "morral", "business", "portatil", "portátil", "laptop", "oficina"],
    "maleta": ["backpack", "morral", "viaje", "bolso", "mochila", "laptop", "oficina"],
    "arquitectura": ["diseno", "diseño", "oficina", "planos", "escritorio", "construccion", "construcción"],
    "construccion": ["obra", "seguridad", "herramienta", "arquitectura", "casco"],
    "ingenieria": ["oficina", "tecnicos", "técnicos", "ingenieria", "ingeniería", "diseno", "diseño"],
    "vip": ["premium", "ejecutivo", "lujo", "alta gama", "exclusivo"],
    "premium": ["lujo", "ejecutivo", "alta gama", "exclusivo", "vip"],
    "eco": ["bambu", "bambú", "reciclado", "reutilizable", "ecologico", "ecológico", "sostenible", "rpet"],
    "ecologico": ["bambu", "bambú", "reciclado", "reutilizable", "sostenible", "eco"],
    "corporativo": ["branding", "oficina", "merchandising", "marca", "empresa"],
    "merchandising": ["branding", "marca", "logo", "promocional", "regalo"],
    "regalo": ["promocional", "obsequio", "detalle", "souvenir", "merchandising"],
    "promocional": ["merchandising", "branding", "logo", "regalo", "obsequio"],
    "tecnologia": ["usb", "cargador", "gadget", "oficina", "auricular", "power bank", "branding"],
    "universidad": ["estudiantes", "educacion", "educación", "oficina", "merchandising"],
    "colegio": ["estudiantes", "educacion", "educación", "infantil", "merchandising"],
    "hospital": ["salud", "medicos", "médicos", "bienestar", "oficina"],
    "financiera": ["corporativo", "ejecutivo", "oficina", "branding", "alta gama"],
    "mujeres": ["belleza", "hogar", "personalizable", "regalo"],
    "hombres": ["tecnologia", "utilidad", "hogar", "oficina"],
    "ninos": ["infantil", "colorido", "didactico", "didáctico", "juguete"],
    "escritura": ["boligrafo", "bolígrafo", "lapiz", "lápiz", "pluma", "oficina"],
    "oficina": ["escritorio", "libreta", "cuaderno", "agenda", "branding"],
    "evento": ["feria", "congreso", "conferencia", "merchandising", "stand"],
    "bienvenida": ["onboarding", "welcome", "kit", "regalo", "oficina"],
    "navidad": ["navideño", "navideña", "fiesta", "regalo", "detalle"],
    "cumpleanos": ["fiesta", "celebra", "party", "regalo", "detalle"],
}


def expand_query(query: str, extra_terms: List[str] = None) -> str:
    """Amplia una consulta con sinonimos y conceptos relacionados.

    No reemplaza la consulta original: conserva los terminos originales y
    anade los relacionados para mejorar el recall del retrieval semantico.
    """
    tokens = query.lower().split()
    added: List[str] = []

    for token in tokens:
        for key, synonyms in SYNONYM_MAP.items():
            if token == key or token in key.split():
                for syn in synonyms:
                    if syn not in tokens and syn not in added:
                        added.append(syn)

    if extra_terms:
        for term in extra_terms:
            if term and term.lower() not in tokens and term.lower() not in added:
                added.append(term.lower())

    expanded = query
    if added:
        expanded = f"{query} {' '.join(added)}"
    return expanded
