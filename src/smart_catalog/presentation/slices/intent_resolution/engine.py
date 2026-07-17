import logging

from ....domain.models.search_intent import SearchIntent
from ....domain.models.structured_search_query import StructuredSearchQuery
from ....shared.dictionaries.product_families import resolve_family, get_family_key

logger = logging.getLogger("smart_catalog.intent")


class IntentResolutionEngine:

    def resolve(self, structured: StructuredSearchQuery) -> SearchIntent:
        types = structured.detected_product_types
        categories = structured.detected_categories
        materials = structured.detected_materials
        price = structured.detected_price_intent
        quality = structured.detected_quality_intent
        eco = structured.detected_eco_intent
        audience = structured.detected_audience

        family = resolve_family(types)
        family_key = get_family_key(types)

        score = 0.0
        reasons: list[str] = []

        has_user_intent = bool(price or quality or eco)
        has_product = bool(types)
        has_category = bool(categories)
        has_material = bool(materials)
        has_audience = bool(audience)

        if has_product and has_audience:
            intent_type = "MIXED"
            score = 0.85
            reasons.append(f"Producto: {types[0]} + audiencia: {audience}")

        elif has_product and has_user_intent:
            intent_type = "MIXED"
            score = 0.85
            reasons.append(f"Producto: {types[0]} + intencion: {price or quality or 'eco'}")

        elif has_product and has_material:
            intent_type = "MIXED"
            score = 0.85
            reasons.append(f"Producto: {types[0]} + material: {materials[0]}")

        elif has_product and not has_user_intent and not has_audience:
            intent_type = "PRODUCT_FAMILY"
            score = 0.9
            reasons.append(f"Familia de producto detectada: {family or types[0]}")

        elif has_category and not has_product and not has_user_intent:
            intent_type = "CATEGORY"
            score = 0.8
            reasons.append(f"Categoria: {categories[0]}")

        elif eco or quality:
            intent_type = "CONCEPT"
            score = 0.7
            concepts = []
            if eco:
                concepts.append("ecologico")
            if quality:
                concepts.append("calidad")
            reasons.append(f"Concepto: {' + '.join(concepts)}")

        elif has_material and not has_product:
            intent_type = "MATERIAL"
            score = 0.75
            reasons.append(f"Material: {materials[0]}")

        elif price and not has_product:
            intent_type = "PRICE"
            score = 0.7
            reasons.append(f"Intencion de precio: {price}")

        elif has_audience and not has_product:
            intent_type = "AUDIENCE"
            score = 0.7
            reasons.append(f"Audiencia: {audience}")

        else:
            intent_type = "UNKNOWN"
            score = 0.3
            reasons.append("Intencion no determinada")

        return SearchIntent(
            intent_type=intent_type,
            confidence=round(score, 2),
            detected_product_family=family or (types[0] if types else None),
            detected_category=categories[0] if categories else None,
            detected_concept="ecologico" if eco else ("calidad" if quality else None),
            detected_audience=audience,
            detected_materials=materials,
            detected_price_intent=price,
            detected_quality_intent=quality,
            reason=" | ".join(reasons),
        )
