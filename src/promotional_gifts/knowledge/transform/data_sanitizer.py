import html
import re
from typing import List

from ...domain.entities.product_knowledge import ProductKnowledge
from ..enrichment.product_html_parser import KNOWN_MATERIALS, SCRAPER_DENYLIST
from .category_resolver import CategoryResolver


# Términos adicionales propios de precios, cotización y logística que no están
# en el denylist del parser.
EXTRA_DENYLIST = {
    "cotización", "cotizacion", "cotiza", "factura", "facturación", "facturacion",
    "proveedor", "importador", "importación", "importacion", "aduana", "flete",
    "seguro", "incoterm", "exworks", "fob", "cif", "despacho aduanero",
    "número de guía", "numero de guia", "rastreo", "seguimiento",
    " SKU", "SKU:", "EAN", "UPC", "REF", "referencia:", "ref:",
}


# Límites razonables para evitar arrastre de texto masivo.
FIELD_LIMITS = {
    "name": 150,
    "description": 1000,
    "characteristics": 1000,
    "price_description": 200,
    "additional_prices": 300,
    "benefits": 500,
    "materials": 200,
    "dimensions": 200,
    "capacity": 100,
    "colors": 200,
    "category": 50,
    "subcategory": 50,
    "recommendations": 500,
    "customization": 300,
    "breadcrumb": 300,
}


class DataSanitizer:
    """Limpieza idempotente de productos ya materializados en ProductKnowledge.

    No depende del scraper: solo trabaja sobre los campos de la entidad.
    """

    def __init__(self) -> None:
        self.resolver = CategoryResolver()
        self.denylist = SCRAPER_DENYLIST | EXTRA_DENYLIST

    def sanitize(self, products: List[ProductKnowledge]) -> List[ProductKnowledge]:
        for product in products:
            product.name = self._sanitize_text(product.name, "name")
            product.characteristics = self._sanitize_text(
                product.characteristics, "characteristics"
            )
            product.description = self._sanitize_text(
                product.description, "description"
            )
            product.price_description = self._sanitize_text(
                product.price_description, "price_description"
            )
            product.additional_prices = self._sanitize_text(
                product.additional_prices, "additional_prices"
            )
            product.benefits = self._sanitize_text(product.benefits, "benefits")
            product.dimensions = self._sanitize_text(product.dimensions, "dimensions")
            product.capacity = self._sanitize_text(product.capacity, "capacity")
            product.colors = self._sanitize_text(product.colors, "colors")
            product.recommendations = self._sanitize_text(
                product.recommendations, "recommendations"
            )
            product.customization = self._sanitize_text(
                product.customization, "customization"
            )
            product.breadcrumb = self._sanitize_text(
                product.breadcrumb, "breadcrumb"
            )

            product.materials = self._sanitize_materials(product.materials)
            if not product.materials:
                product.materials = self._infer_materials_from_text(
                    f"{product.description} {product.characteristics} {product.name}"
                )

            # Resolver categoría y subcategoría de forma determinista.
            product.category, product.subcategory = self.resolver.resolve(product)

        return products

    def _sanitize_text(self, value: str, field: str) -> str:
        if not value or value.lower() == "nan":
            return ""
        # Decodificar entidades HTML y descartar etiquetas residuales.
        text = html.unescape(str(value))
        text = re.sub(r"<[^>]+>", " ", text)
        # Quitar URLs.
        text = re.sub(r"https?://\S+", " ", text)
        text = re.sub(r"www\.\S+", " ", text)

        # Descartar fragmentos con términos no deseados.
        fragments = [
            f.strip() for f in text.replace("\r", "\n").split("\n") if f.strip()
        ]
        if not fragments:
            fragments = [
                s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()
            ]
        clean_fragments = []
        for fragment in fragments:
            lower = fragment.lower()
            if any(deny in lower for deny in self.denylist):
                continue
            clean_fragments.append(fragment)
        text = " ".join(clean_fragments)
        text = " ".join(text.split())

        # Truncar si excede el límite.
        limit = FIELD_LIMITS.get(field, 500)
        if len(text) > limit:
            text = text[:limit].rsplit(" ", 1)[0]
        return text.strip()

    def _sanitize_materials(self, value: str) -> str:
        if not value or value.lower() == "nan":
            return ""
        return self._extract_material_terms(value)

    def _infer_materials_from_text(self, text: str) -> str:
        if not text or text.lower() == "nan":
            return ""
        return self._extract_material_terms(text)

    def _extract_material_terms(self, text: str) -> str:
        lower = text.lower()
        found = set()
        ordered = sorted(KNOWN_MATERIALS, key=len, reverse=True)
        for term in ordered:
            if re.search(re.escape(term), lower):
                found.add(term)
        if not found:
            return ""

        def _present(term: str) -> str:
            if term in {"rpet", "pvc", "eva", "tpr"}:
                return term.upper()
            if term == "acero inoxidable":
                return "acero inoxidable"
            return term

        result = ", ".join(_present(t) for t in sorted(found))
        return result[: FIELD_LIMITS.get("materials", 200)]
