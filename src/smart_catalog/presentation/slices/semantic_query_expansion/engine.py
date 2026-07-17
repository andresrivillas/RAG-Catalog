import logging
import time
from typing import Optional

from ....domain.models.expanded_search_query import ExpandedSearchQuery
from ....domain.models.search_intent import SearchIntent
from ....domain.models.structured_search_query import StructuredSearchQuery
from ....shared.product_family_dictionary import get_family_expansions, get_family_key
from .dictionaries import (
    PRODUCT_EXPANSIONS,
    MATERIAL_EXPANSIONS,
    CATEGORY_EXPANSIONS,
    QUALITY_EXPANSIONS,
    PRICE_LOW_EXPANSIONS,
    PRICE_HIGH_EXPANSIONS,
    ECO_EXPANSIONS,
    ATTRIBUTE_EXPANSIONS,
    COLOR_EXPANSIONS,
)

logger = logging.getLogger("smart_catalog.expansion")

MAX_TERMS = 15


class SemanticQueryExpansionEngine:

    def expand(
        self,
        structured: StructuredSearchQuery,
        intent: Optional[SearchIntent] = None,
    ) -> ExpandedSearchQuery:
        start = time.perf_counter()

        terms: list[str] = []
        reasons: list[str] = []

        if (
            intent
            and intent.intent_type == "PRODUCT_FAMILY"
            and intent.detected_product_family
        ):
            family_key = get_family_key(structured.detected_product_types)
            if family_key:
                family_terms = get_family_expansions(family_key)
                if family_terms:
                    terms.extend(family_terms)
                    reasons.append(f"familia:{intent.detected_product_family}")
        elif structured.detected_product_types:
            for ptype in structured.detected_product_types:
                expanded = PRODUCT_EXPANSIONS.get(ptype.upper(), [])
                if expanded:
                    family_key = get_family_key([ptype])
                    if family_key:
                        family_terms = get_family_expansions(family_key)
                        terms.extend(family_terms[:5])
                        reasons.append(f"familia:{ptype}")
                    else:
                        terms.extend(expanded[:5])
                        reasons.append(f"producto:{ptype}")

        if (
            intent
            and intent.intent_type == "PRODUCT_FAMILY"
        ):
            pass
        else:
            if structured.detected_materials:
                for mat in structured.detected_materials:
                    expanded = MATERIAL_EXPANSIONS.get(mat.upper(), [])
                    if expanded:
                        terms.extend(expanded[:3])
                        reasons.append(f"material:{mat}")

            if structured.detected_categories:
                for cat in structured.detected_categories:
                    expanded = CATEGORY_EXPANSIONS.get(cat, [])
                    if expanded:
                        terms.extend(expanded[:3])
                        reasons.append(f"categoria:{cat}")

        is_product = (
            intent
            and intent.intent_type == "PRODUCT_FAMILY"
        )

        if not is_product:
            if structured.detected_eco_intent:
                terms.extend(ECO_EXPANSIONS[:3])
                reasons.append("eco")

            if structured.detected_quality_intent == "HIGH_QUALITY":
                terms.extend(QUALITY_EXPANSIONS[:3])
                reasons.append("calidad")

            if structured.detected_price_intent == "LOW_PRICE":
                terms.extend(PRICE_LOW_EXPANSIONS[:3])
                reasons.append("precio:bajo")
            elif structured.detected_price_intent == "HIGH_PRICE":
                terms.extend(PRICE_HIGH_EXPANSIONS[:3])
                reasons.append("precio:alto")

        if structured.detected_colors:
            for color in structured.detected_colors:
                expanded = COLOR_EXPANSIONS.get(color.upper(), [])
                if expanded:
                    terms.extend(expanded[:2])
                    reasons.append(f"color:{color}")

        if structured.detected_attributes:
            for attr in structured.detected_attributes:
                expanded = ATTRIBUTE_EXPANSIONS.get(attr.upper(), [])
                if expanded:
                    terms.extend(expanded[:2])
                    reasons.append(f"atributo:{attr}")

        seen: set[str] = set()
        deduped: list[str] = []
        for term in terms:
            t = term.lower().strip()
            if t not in seen:
                seen.add(t)
                deduped.append(t)

        deduped = deduped[:MAX_TERMS]

        base_tokens = structured.normalized_query.split()
        expanded_tokens = [t for t in deduped if t not in base_tokens]

        all_tokens = base_tokens + expanded_tokens
        expanded_query = " ".join(all_tokens)

        total_possible = (
            (1 if structured.detected_product_types else 0)
            + len(structured.detected_materials)
            + len(structured.detected_categories)
            + (1 if structured.detected_eco_intent else 0)
            + (1 if structured.detected_quality_intent else 0)
            + (1 if structured.detected_price_intent else 0)
            + (1 if structured.detected_colors else 0)
            + (1 if structured.detected_attributes else 0)
        )
        expanded_domains = len(set(reasons)) if reasons else 0
        confidence = round(
            min(1.0, 0.5 + 0.3 * (expanded_domains / max(total_possible, 1))),
            2,
        ) if total_possible > 0 else structured.confidence

        elapsed = (time.perf_counter() - start) * 1000

        logger.info(
            "Expansion: '%s' -> '%s' | +%d terminos | dominios: %s | confianza: %.2f | tiempo: %.1fms",
            structured.original_query, expanded_query,
            len(expanded_tokens), reasons, confidence, elapsed,
        )

        return ExpandedSearchQuery(
            original_query=structured.original_query,
            normalized_query=structured.normalized_query,
            expanded_terms=expanded_tokens,
            expanded_query=expanded_query,
            expansion_reason=" | ".join(reasons) if reasons else "sin expansion",
            confidence=confidence,
            structured_query=structured,
        )
