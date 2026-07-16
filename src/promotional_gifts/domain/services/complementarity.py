"""Complementariedad de productos.

Los productos de un kit deben complementarse, no competir. Esta utilidad
calcula qué tanto dos productos (o un kit completo) se complementan en lugar
de ser redundantes.
"""

from typing import List

from ..entities.product_knowledge import ProductKnowledge

# Categorias que compiten entre si (mismo proposito).
REDUNDANT_CATEGORIES = {
    "escritura", "bolsos", "hogar", "tecnologia", "oficina", "viaje",
}

# Roles que cubren el mismo nicho comercial.
ROLE_CLUSTERS = {
    "escritura": {"CORE", "UTILITY", "PROMOTIONAL", "ACCESSORY"},
    "oficina": {"CORE", "UTILITY", "PROMOTIONAL", "ACCESSORY"},
    "viaje": {"CORE", "UTILITY", "ACCESSORY"},
    "hogar": {"CORE", "UTILITY", "PROMOTIONAL"},
}


def _category(product: ProductKnowledge) -> str:
    text = f"{product.name} {product.description}".lower()
    mapping = {
        "escritura": ["lapiz", "boligrafo", "bolígrafo", "resaltador", "pluma", "portaminas", "sticky", "nota"],
        "bolsos": ["bolsa", "mochila", "cartera", "estuche"],
        "hogar": ["taza", "mug", "termo", "vaso", "plat", "copa", "toalla"],
        "tecnologia": ["usb", "cargador", "auricular", "altavoz", "speaker", "power bank"],
        "oficina": ["libreta", "cuaderno", "carpeta", "agenda", "notas"],
        "viaje": ["paraguas", "maleta", "neceser", "viaje"],
    }
    for category, keywords in mapping.items():
        if any(kw in text for kw in keywords):
            return category
    return "otros"


def products_complement(a: ProductKnowledge, b: ProductKnowledge) -> float:
    """Score 0..1: 1 = se complementan, 0 = redundantes/compiten."""
    cat_a = _category(a)
    cat_b = _category(b)
    if cat_a == cat_b and cat_a in REDUNDANT_CATEGORIES:
        return 0.2
    if cat_a == cat_b and cat_a == "otros":
        return 0.6
    # Diferentes categorias suelen complementarse.
    return 0.9


def kit_complementarity(products: List[ProductKnowledge]) -> float:
    """Score 0..1 de complementariedad del kit completo."""
    if len(products) < 2:
        return 0.5
    total = 0.0
    pairs = 0
    for i in range(len(products)):
        for j in range(i + 1, len(products)):
            total += products_complement(products[i], products[j])
            pairs += 1
    return total / pairs if pairs else 0.5
