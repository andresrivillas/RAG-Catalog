from typing import Optional


def generate(product, intent, role: Optional[str], trace, concept: Optional[str] = None) -> str:
    """Genera una razón corta (máximo 2 oraciones) de por qué un producto
    encaja en la propuesta. Usa el contexto de industria, concepto y material.
    """
    parts = []

    industry = getattr(intent, "industry", None) if intent else None
    affinity = getattr(trace, "affinity_score", 0.0) if trace else 0.0
    category = getattr(product, "category", "") or ""
    materials = getattr(product, "materials", "") or ""
    tags = {t.lower() for t in (getattr(product, "commercial_tags", []) or [])}
    name = getattr(product, "name", "Producto")
    value_level = getattr(product, "perceived_value_level", "medio")

    # Primera oración: anclar al contexto.
    if industry and affinity >= 0.75:
        if concept:
            parts.append(
                f"{name} refuerza el concepto de '{concept}' y se alinea con el sector {industry}."
            )
        else:
            parts.append(
                f"{name} se alinea con el sector {industry} ({category or 'categoría adecuada'})."
            )
    elif industry and affinity >= 0.55:
        parts.append(f"{name} complementa una propuesta pensada para el sector {industry}.")
    elif concept:
        parts.append(f"{name} aporta coherencia al concepto de '{concept}'.")
    else:
        parts.append(f"{name} aporta coherencia al kit.")

    role = role or "CANDIDATE"
    role_sentences = {
        "CORE": "Funciona como pieza central de la propuesta.",
        "PREMIUM": "Aporta exclusividad y eleva la percepción de marca.",
        "UTILITY": "No solo aporta utilidad diaria; también prolonga la exposición de la marca.",
        "PROMOTIONAL": "Refuerza la marca del cliente de forma visible y constante.",
        "ACCESSORY": "Complementa el kit sin restar protagonismo.",
        "PACKAGING": "Presenta el regalo de forma ordenada y profesional.",
    }
    role_sentence = role_sentences.get(role, "Complementa la propuesta comercial.")

    extras = []
    if "eco" in tags or "ecologico" in tags or "sostenible" in tags or "rpet" in tags:
        extras.append("opción eco")
    if "personalizable" in tags or (getattr(product, "customization", "") or "").strip():
        extras.append("personalizable")
    if "premium" in tags or value_level == "alto":
        extras.append("alta gama")
    if materials:
        extras.append(materials)

    if extras:
        role_sentence = role_sentence[:-1] + f" ({', '.join(extras)})."

    parts.append(role_sentence)
    return " ".join(parts[:2])
