from typing import Optional

from .models import CatalogQuality, DetectedProblem


def generate_recommendations(
    quality: CatalogQuality,
    product: dict,
    enrichment_confidence: Optional[float] = None,
) -> list[str]:
    recs: list[str] = []

    if not quality.has_description:
        recs.append("Agregar descripcion del producto incluyendo materiales, uso y beneficios.")

    if not quality.has_materials:
        recs.append("Agregar material principal (ej: acero inoxidable, RPET, bambu, plastico).")

    if quality.category_is_generic:
        current = product.get("category", "")
        recs.append(f"Reclasificar categoria '{current}' a una mas especifica (Tecnologia, Oficina, Eco, etc.).")

    if not quality.has_tags:
        recs.append("Agregar tags comerciales (ej: premium, ecologico, corporativo, ejecutivo).")

    if not quality.has_colors:
        recs.append("Agregar colores disponibles para facilitar busquedas por color.")

    if not validate_field_exists(product, "occasion_tags"):
        recs.append("Agregar ocasiones de uso (eventos, ferias, bienvenida, capacitacion).")

    if not validate_field_exists(product, "audience_tags"):
        recs.append("Agregar perfiles de cliente objetivo (ejecutivo, profesional, estudiante).")

    if not quality.has_family:
        recs.append("El producto no tiene una familia comercial asignada.")

    if not quality.has_commercial_knowledge_strong:
        name = product.get("name", "")
        cat = product.get("category", "")
        if "tecnologia" in cat.lower() or any(w in name.lower() for w in ["usb", "bluetooth", "cargador"]):
            recs.append("Agregar atributos tecnologicos (bluetooth, USB, inalambrico, recargable).")
        if any(w in name.lower() for w in ["eco", "rpet", "bambu", "reciclado"]):
            recs.append("Agregar atributos ecologicos (material reciclado, sostenible, biodegradable).")

    if enrichment_confidence and enrichment_confidence < 0.3:
        recs.append("Sin informacion suficiente para inferir perfil comercial automaticamente. Enriquecer datos del producto.")

    for problem in quality.detected_problems:
        if problem.code == "potential_misclassification" and problem.suggestion not in recs:
            recs.append(f"Revisar clasificacion: {problem.description}.")

    if not recs:
        recs.append("Producto con informacion adecuada.")

    return recs


def generate_recommendations_text(quality: CatalogQuality, product: dict) -> list[str]:
    recs: list[str] = []
    if not quality.has_description:
        recs.append("Agregar descripcion del producto.")
    if not quality.has_materials:
        recs.append("Agregar materiales.")
    if quality.category_is_generic:
        recs.append("Reclasificar categoria.")
    if not quality.has_tags:
        recs.append("Agregar tags comerciales.")
    if not quality.has_commercial_knowledge_strong:
        recs.append("Mejorar perfil comercial.")
    if quality.evidence_score < 0.2:
        recs.append("Agregar informacion para mejorar inferencia.")
    for p in quality.detected_problems:
        if p.code == "potential_misclassification":
            recs.append(f"Revisar clasificacion: {p.description}.")
    if not recs:
        recs.append("Completar campos opcionales.")
    return recs[:5]


from .validators import validate_field_exists
