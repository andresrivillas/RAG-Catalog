import logging
from typing import Optional

from ....domain.models.structured_search_query import StructuredSearchQuery
from .normalizer import QueryNormalizer, SYNONYM_MAP, GENERIC_TERMS
from .detectors import material, category, color, attribute, audience, intent
from .detectors.confidence import calculate_confidence
from .detectors.capacity import detect_capacity
from .detectors.technology import detect_technologies

logger = logging.getLogger("smart_catalog.query_understanding")


class QueryUnderstandingEngine:

    def __init__(self) -> None:
        self._normalizer = QueryNormalizer()

    def understand(self, text: str) -> StructuredSearchQuery:
        original = text.strip()
        normalized = self._normalizer.normalize(text)

        tokens = normalized.split()
        content_tokens = self._normalizer.remove_digits(
            self._normalizer.remove_stop_words(tokens)
        )

        synonym_tokens = self._normalizer.apply_synonyms(content_tokens)
        product_types = self._normalizer.detect_product_types(content_tokens)
        materials = material.detect_materials(content_tokens)
        price_intent = intent.detect_price_intent(content_tokens)
        quality_intent = intent.detect_quality_intent(content_tokens)
        eco_intent = intent.detect_eco_intent(content_tokens)
        categories = category.detect_categories(content_tokens)
        colors = color.detect_colors(content_tokens)
        aud = audience.detect_audience(normalized)
        attrs = attribute.detect_attributes(content_tokens)
        capacity = detect_capacity(content_tokens, original)
        technologies = detect_technologies(original)

        known_tokens: set[str] = set()
        for t in content_tokens:
            if t in SYNONYM_MAP or material.is_known(t) or category.is_known(t) \
               or color.is_known(t) or attribute.is_known(t) or intent.is_known(t):
                known_tokens.add(t)

        for mt in audience.matched_terms(normalized):
            known_tokens.add(mt)

        known_count = len(known_tokens)
        unknown = [t for t in content_tokens if t not in known_tokens and t not in GENERIC_TERMS]

        confidence = calculate_confidence(
            content_tokens, known_count, product_types, materials, price_intent, categories,
        )

        normalized_query = " ".join(synonym_tokens)

        logger.info(
            "Consulta original: '%s' | normalizada: '%s' | productos: %s | "
            "materiales: %s | precio: %s | calidad: %s | eco: %s | categorias: %s | "
            "colores: %s | audiencia: %s | confianza: %.2f",
            original, normalized_query,
            product_types, materials, price_intent, quality_intent, eco_intent,
            categories, colors, aud, confidence,
        )

        return StructuredSearchQuery(
            original_query=original,
            normalized_query=normalized_query,
            detected_categories=categories,
            detected_capacity=capacity,
            detected_technologies=technologies,
            detected_materials=materials,
            detected_price_intent=price_intent,
            detected_quality_intent=quality_intent,
            detected_eco_intent=eco_intent,
            detected_product_types=product_types,
            detected_audience=aud,
            detected_colors=colors,
            detected_attributes=attrs,
            unknown_terms=unknown,
            confidence=confidence,
        )
