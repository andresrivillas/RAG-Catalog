import logging
from typing import Optional

from ....domain.models.catalog_product import CatalogProduct
from ....domain.models.expanded_search_query import ExpandedSearchQuery
from ....domain.models.search_explanation import SearchExplanation
from ....domain.models.search_intent import SearchIntent
from ....domain.models.structured_search_query import StructuredSearchQuery
from ....shared.dictionaries.product_families import is_product_in_family, get_family_key

logger = logging.getLogger("smart_catalog.explanation")

PRIORITY_MAP: dict[str, int] = {
    "family": 0,
    "material": 1,
    "eco": 2,
    "category": 3,
    "price": 4,
    "quality": 5,
    "attribute": 6,
    "semantic": 7,
}


class SearchExplanationEngine:

    def explain(
        self,
        structured: StructuredSearchQuery,
        expanded: Optional[ExpandedSearchQuery],
        product: CatalogProduct,
        relevance_score: float,
        intent: Optional[SearchIntent] = None,
    ) -> SearchExplanation:
        reasons: list[tuple[int, str]] = []
        matched_attrs: list[str] = []
        matched_materials: list[str] = []
        matched_cats: list[str] = []
        matched_colors: list[str] = []

        product_material = product.material.lower()
        product_category = product.category.lower()
        product_name = product.name.lower()

        if intent and intent.intent_type == "PRODUCT_FAMILY":
            family_key = get_family_key(structured.detected_product_types)
            if family_key and is_product_in_family(product_name, product_category, family_key):
                reasons.append(
                    (PRIORITY_MAP["family"],
                     "Coincide exactamente con la familia de productos solicitada")
                )

        if structured.detected_materials:
            for mat in structured.detected_materials:
                if mat.lower() in product_material:
                    matched_materials.append(mat)
                    reasons.append(
                        (PRIORITY_MAP["material"], f"Fabricado en {mat.lower()}")
                    )

        if structured.detected_categories:
            for cat in structured.detected_categories:
                if cat.lower() in product_category or cat.lower() in product_name:
                    matched_cats.append(cat)
                    reasons.append(
                        (PRIORITY_MAP["category"], f"Pertenece a {cat}")
                    )

        if structured.detected_product_types:
            for pt in structured.detected_product_types:
                if pt.lower() in product_name or pt.lower() in product_category:
                    if pt not in matched_cats:
                        matched_cats.append(pt)
                        reasons.append(
                            (PRIORITY_MAP["category"],
                             f"Coincide con el tipo {pt.lower()}")
                        )

        if structured.detected_eco_intent:
            eco_match = product.eco_friendly or any(
                m in product_material for m in ["rpet", "bambu", "corcho"]
            )
            if eco_match:
                matched_attrs.append("ecologico")
                reasons.append(
                    (PRIORITY_MAP["eco"], "Producto ecologico y sostenible")
                )

        if structured.detected_price_intent:
            if structured.detected_price_intent == "LOW_PRICE":
                matched_attrs.append("precio_bajo")
                reasons.append(
                    (PRIORITY_MAP["price"], "Entre las opciones de menor precio")
                )
            elif structured.detected_price_intent == "HIGH_PRICE":
                matched_attrs.append("precio_alto")
                reasons.append(
                    (PRIORITY_MAP["price"], "Precio dentro del segmento alto")
                )

        if structured.detected_quality_intent == "HIGH_QUALITY":
            matched_attrs.append("premium")
            reasons.append(
                (PRIORITY_MAP["quality"], "Clasificado como producto premium")
            )

        if structured.detected_colors:
            for color in structured.detected_colors:
                if color.lower() in product_name or color.lower() in product.colors.lower():
                    matched_colors.append(color)
                    reasons.append(
                        (PRIORITY_MAP["attribute"], f"Color {color.lower()} solicitado")
                    )

        if structured.detected_attributes:
            name_desc = f"{product_name} {product.description.lower()}"
            for attr in structured.detected_attributes:
                if attr.lower() in name_desc:
                    matched_attrs.append(attr.lower())

        if relevance_score > 0.5:
            reasons.append(
                (PRIORITY_MAP["semantic"], "Alta relevancia semantica")
            )
        elif relevance_score > 0.2:
            reasons.append(
                (PRIORITY_MAP["semantic"], "Buena similitud semantica")
            )

        reasons.sort(key=lambda x: x[0])

        secondary = [r[1] for r in reasons]
        primary = secondary[0] if secondary else "Relevante para la consulta"

        summary = self._build_summary(
            primary, matched_materials, matched_cats, matched_attrs,
            structured, relevance_score,
        )

        confidence = round(min(1.0, 0.3 + 0.15 * len(reasons)), 2)

        return SearchExplanation(
            reason=primary,
            primary_reason=primary,
            secondary_reasons=secondary[1:],
            matched_attributes=matched_attrs,
            matched_materials=matched_materials,
            matched_categories=matched_cats,
            matched_price_intent=structured.detected_price_intent,
            matched_quality_intent=structured.detected_quality_intent,
            matched_eco_intent=structured.detected_eco_intent,
            matched_colors=matched_colors,
            confidence=confidence,
            summary=summary,
        )

    def _build_summary(
        self,
        primary: str,
        materials: list[str],
        categories: list[str],
        attributes: list[str],
        structured: StructuredSearchQuery,
        score: float,
    ) -> str:
        parts: list[str] = []

        if "familia" in primary.lower():
            parts.append("Coincide con la familia de productos solicitada")
        elif materials and categories:
            parts.append("Coincide con material y categoria solicitados")
        elif materials:
            parts.append("Coincide con el material solicitado")
        elif categories:
            parts.append("Dentro de la categoria buscada")

        if "ecologico" in attributes or structured.detected_eco_intent:
            parts.append("Producto ecologico")
        if "premium" in attributes:
            parts.append("Opcion premium")
        if "precio_bajo" in attributes:
            parts.append("Precio competitivo")
        elif "precio_alto" in attributes:
            parts.append("Producto de alta gama")

        if score > 0.7:
            parts.append("Altamente relacionado")
        elif score > 0.4:
            parts.append("Muy relacionado")

        if not parts:
            parts.append("Relevante para la consulta")

        summary = " | ".join(parts)
        return summary[:120]
