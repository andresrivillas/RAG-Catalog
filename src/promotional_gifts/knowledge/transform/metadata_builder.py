import re
from typing import List

from ...domain.entities.product_knowledge import ProductKnowledge

OCCASION_RULES = {
    "cumpleanos": ["cumple", "fiesta", "celebra", "party"],
    "navidad": ["navidad", "navideño", "navideña", "christmas"],
    "bienvenida": ["bienvenida", "welcome", "onboarding", "recepcion"],
    "evento": ["evento", "feria", "congreso", "conferencia"],
    "campana": ["campaña", "campana", "marketing", "promocion", "promoción"],
    "reconocimiento": ["premio", "reconocimiento", "logro", "empleado"],
}

AUDIENCE_RULES = {
    "mujeres": ["mujer", "mujeres", "femenino", "femenina"],
    "hombres": ["hombre", "hombres", "masculino", "masculina"],
    "ninos": ["niño", "niña", "niños", "niñas", "infantil", "kids"],
    "vip": ["premium", "exclusivo", "lujo", "vip", "alta gama"],
    "corporativo": ["empresa", "oficina", "corporativo", "negocio", "cliente"],
}

COMMERCIAL_RULES = {
    "eco": ["eco", "ecologico", "ecológico", "sostenible", "rpet", "recicl"],
    "personalizable": [
        "logo",
        "grabado",
        "personaliz",
        "marca",
        "tampografia",
        "tampografía",
        "sublimacion",
        "sublimación",
    ],
    "tecnologico": ["usb", "cargador", "auricular", "altavoz", "bluetooth"],
    "hogar": ["taza", "mug", "termo", "vaso", "cocina", "hogar"],
}


class MetadataBuilder:
    def build(self, products: List[ProductKnowledge]) -> List[ProductKnowledge]:
        median_price = self._median_price(products)
        for product in products:
            self._build_keywords(product)
            product.occasion_tags = self._match(OCCASION_RULES, product)
            product.audience_tags = self._match(AUDIENCE_RULES, product)
            product.commercial_tags = self._match(COMMERCIAL_RULES, product)
            product.perceived_value_level = self._perceived_value(
                product, median_price
            )
            product.embedding_text = self._build_searchable_text(product)
        return products

    def _median_price(self, products: List[ProductKnowledge]) -> float:
        prices = [p.price.amount for p in products if p.price.amount > 0]
        if not prices:
            return 0.0
        prices.sort()
        n = len(prices)
        return prices[n // 2]

    def _build_keywords(self, product: ProductKnowledge) -> None:
        # Se construyen a partir de campos ya limpios y comercialmente útiles.
        text = (
            f"{product.name} {product.category} {product.subcategory} "
            f"{product.benefits} {product.materials} "
            f"{' '.join(product.commercial_tags)} {' '.join(product.audience_tags)}"
        ).lower()
        tokens = re.findall(r"[a-z0-9áéíóúñ]+", text)
        stop = {
            "de", "la", "el", "en", "con", "para", "y", "por", "un", "una",
            "con", "del", "los", "las", "su", "se", "es", "al", "que",
            "con", "sin", "sobre", "entre", "desde", "hasta", "cada",
        }
        keywords = [t for t in tokens if len(t) > 2 and t not in stop]
        product.keywords = list(dict.fromkeys(keywords))[:15]

    def _match(self, rules: dict, product: ProductKnowledge) -> List[str]:
        text = (
            f"{product.name} {product.category} {product.subcategory} "
            f"{product.benefits} {product.materials} {product.customization} "
            f"{' '.join(product.commercial_tags)}"
        ).lower()
        return [tag for tag, kws in rules.items() if any(kw in text for kw in kws)]

    def _perceived_value(
        self, product: ProductKnowledge, median_price: float
    ) -> str:
        score = 0
        if median_price > 0 and product.price.amount >= median_price * 1.5:
            score += 2
        elif median_price > 0 and product.price.amount >= median_price:
            score += 1
        text = f"{product.name} {product.materials} {product.benefits}".lower()
        if any(m in text for m in ["cuero", "acero", "madera", "aluminio", "vidrio", "cristal"]):
            score += 2
        if any(u in text for u in ["reusable", "plegable", "multiusos", "termo", "portatil", "portátil"]):
            score += 1
        if len(product.benefits) >= 30:
            score += 1
        if score >= 5:
            return "alto"
        if score >= 3:
            return "medio"
        return "bajo"

    def _build_searchable_text(self, product: ProductKnowledge) -> str:
        # Embedding text con información comercial útil exclusivamente.
        # No URLs, precios, inventario, fechas, logística, HTML ni imágenes.
        parts = [
            f"Nombre: {product.name}",
            f"Categoría: {product.category}",
            f"Subcategoría: {product.subcategory}",
            f"Beneficios: {product.benefits}",
            f"Materiales: {product.materials}",
            f"Keywords: {' '.join(product.keywords)}",
            f"Etiquetas comerciales: {' '.join(product.commercial_tags)}",
            f"Ocasiones: {' '.join(product.occasion_tags)}",
            f"Público: {' '.join(product.audience_tags)}",
        ]
        return "\n".join(
            p for p in parts
            if len(p.split(": ", 1)) > 1 and p.split(": ", 1)[1].strip()
        )
