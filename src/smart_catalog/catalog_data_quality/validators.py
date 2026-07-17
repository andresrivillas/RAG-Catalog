from typing import Optional

from .models import DetectedProblem

GENERIC_CATEGORIES = frozenset({
    "otros", "general", "varios", "sin categoria", "accesorios",
    "complementos", "variedad", "surtido",
})

UNKNOWN_MATERIALS = frozenset({
    "eva", "pvc", "mesh", "malla", "metalizado", "carton",
})

AMBIGUOUS_CATEGORIES = frozenset({
    "hogar", "accesorios", "textiles", "varios",
})

REQUIRED_FIELDS = [
    ("name", "nombre"),
    ("category", "categoria"),
]

STRONGLY_RECOMMENDED_FIELDS = [
    ("description", "descripcion"),
    ("commercial_tags", "tags comerciales"),
]

RECOMMENDED_FIELDS = [
    ("colors", "colores"),
    ("occasion_tags", "tags de ocasion"),
    ("audience_tags", "tags de audiencia"),
    ("benefits", "beneficios"),
    ("subcategory", "subcategoria"),
    ("characteristics", "caracteristicas"),
]


NAME_IS_REFERENCE_PATTERNS = [
    lambda n: len(n.split()) <= 2 and all(c.isupper() or c.isdigit() or c in "-/:." for c in n),
    lambda n: any(c.isdigit() for c in n) and len(n) < 8,
]


def validate_field_exists(product: dict, field: str) -> bool:
    val = product.get(field)
    if val is None:
        return False
    if isinstance(val, str) and not val.strip():
        return False
    if isinstance(val, (list, tuple)) and len(val) == 0:
        return False
    return True


def validate_materials(product: dict) -> tuple[bool, list[str]]:
    raw = product.get("materials", "")
    if not raw or not raw.strip():
        return False, []
    parts = [m.strip().lower() for m in raw.split(",") if m.strip()]
    valid = [m for m in parts if m not in UNKNOWN_MATERIALS]
    return True, valid


def validate_category(product: dict) -> tuple[bool, bool, Optional[str]]:
    cat = (product.get("category") or "").strip()
    if not cat:
        return False, True, None
    is_generic = cat.lower() in GENERIC_CATEGORIES
    is_ambiguous = cat.lower() in AMBIGUOUS_CATEGORIES
    return True, is_generic, "ambiguo" if is_ambiguous else ("generico" if is_generic else "valida")


def validate_price(product: dict) -> Optional[str]:
    price = product.get("price")
    if price is None or price == 0:
        return "sin_precio"
    if price < 100:
        return "precio_muy_bajo"
    if price > 900000:
        return "precio_muy_alto"
    return None


def validate_name(product: dict) -> Optional[str]:
    name = (product.get("name") or "").strip()
    if not name:
        return "nombre_vacio"
    for pattern in NAME_IS_REFERENCE_PATTERNS:
        if pattern(name):
            return "nombre_parece_referencia"
    return None


def detect_duplicates(products: list[dict]) -> dict[str, list[str]]:
    seen: dict[str, list[str]] = {}
    for p in products:
        name = (p.get("name") or "").strip().lower()
        if name and len(name) > 5:
            if name not in seen:
                seen[name] = []
            seen[name].append(p.get("reference", ""))
    return {name: refs for name, refs in seen.items() if len(refs) > 1}


def detect_potential_misclassification(product: dict) -> Optional[str]:
    name = (product.get("name") or "").lower()
    cat = (product.get("category") or "").lower()
    sub = (product.get("subcategory") or "").lower()

    if "usb" in name or "cargador" in name or "bluetooth" in name:
        if "tecnologia" not in cat and "electronica" not in cat and cat != "tecnología":
            return "podria ser Tecnologia"
    if "rpet" in name or "bambu" in name or "ecologico" in name or "eco" in name:
        if "eco" not in cat and "sostenible" not in cat:
            return "podria ser Eco" if cat != "eco" else None
    if "lapicero" in name or "boligrafo" in name or "esfero" in name:
        if "escritura" not in cat and "papeleria" not in cat:
            return "podria ser Escritura"
    if "termo" in name or "botella" in name or "botilito" in name:
        if "termos" not in cat and "bebidas" not in cat:
            return "podria ser Termos"
    return None


def validate_product(product: dict) -> list[DetectedProblem]:
    problems: list[DetectedProblem] = []

    for field, label in REQUIRED_FIELDS:
        if not validate_field_exists(product, field):
            problems.append(DetectedProblem(
                code=f"missing_{field}",
                severity="high",
                field=field,
                description=f"Falta {label}",
                suggestion=f"Agregar {label}",
            ))

    for field, label in STRONGLY_RECOMMENDED_FIELDS:
        if not validate_field_exists(product, field):
            problems.append(DetectedProblem(
                code=f"missing_{field}",
                severity="medium",
                field=field,
                description=f"Sin {label}",
                suggestion=f"Agregar {label}",
            ))

    for field, label in RECOMMENDED_FIELDS:
        if not validate_field_exists(product, field):
            problems.append(DetectedProblem(
                code=f"missing_{field}",
                severity="low",
                field=field,
                description=f"Sin {label}",
                suggestion=f"Agregar {label}",
            ))

    has_mats, valid_mats = validate_materials(product)
    if not has_mats:
        problems.append(DetectedProblem(
            code="missing_materials",
            severity="high",
            field="materials",
            description="Sin materiales",
            suggestion="Agregar material principal",
        ))

    has_cat, is_generic, cat_status = validate_category(product)
    if is_generic:
        problems.append(DetectedProblem(
            code="generic_category",
            severity="high",
            field="category",
            description=f"Categoria generica: {product.get('category')}",
            suggestion="Reclasificar a una categoria especifica",
        ))

    name_issue = validate_name(product)
    if name_issue == "nombre_vacio":
        problems.append(DetectedProblem(
            code="empty_name", severity="high", field="name",
            description="Nombre vacio", suggestion="Asignar nombre descriptivo",
        ))
    elif name_issue == "nombre_parece_referencia":
        problems.append(DetectedProblem(
            code="name_looks_like_reference", severity="medium", field="name",
            description="Nombre parece codigo de referencia",
            suggestion="Asignar nombre comercial descriptivo",
        ))

    price_issue = validate_price(product)
    if price_issue == "sin_precio":
        problems.append(DetectedProblem(
            code="missing_price", severity="high", field="price",
            description="Sin precio", suggestion="Agregar precio",
        ))
    elif price_issue:
        problems.append(DetectedProblem(
            code=price_issue, severity="low", field="price",
            description=f"Precio inusual: {product.get('price')}",
            suggestion="Verificar precio",
        ))

    misclass = detect_potential_misclassification(product)
    if misclass:
        problems.append(DetectedProblem(
            code="potential_misclassification", severity="medium",
            field="category", description=misclass,
            suggestion="Revisar clasificacion",
        ))

    return problems


def find_missing_fields(product: dict) -> list[str]:
    missing: list[str] = []
    for field, label in REQUIRED_FIELDS + STRONGLY_RECOMMENDED_FIELDS + RECOMMENDED_FIELDS:
        if not validate_field_exists(product, field):
            missing.append(field)
    return missing


def suggest_priority_fields(product: dict) -> list[str]:
    suggested: list[str] = []
    if not validate_field_exists(product, "materials"):
        suggested.append("materiales")
    if not validate_field_exists(product, "description"):
        suggested.append("descripcion")
    if not validate_field_exists(product, "commercial_tags"):
        suggested.append("tags comerciales")
    if not validate_field_exists(product, "colors"):
        suggested.append("colores")
    cat = (product.get("category") or "").strip().lower()
    if cat in GENERIC_CATEGORIES:
        suggested.append("categoria especifica")
    return suggested
