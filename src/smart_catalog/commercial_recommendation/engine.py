import logging
from typing import Optional

from ..domain.models.structured_search_query import StructuredSearchQuery
from .models import RecommendationOutput
from .knowledge import (
    get_audience_rules,
    get_category_rules,
    get_technology_rules,
    get_price_rules,
    get_quality_rules,
)

logger = logging.getLogger("smart_catalog.recommendation")

NON_ECO_MATERIALS = frozenset({
    "PLASTICO", "PVC", "POLIESTER", "POLIPROPILENO",
    "SINTETICO", "NEOPRENO", "CAUCHO", "GOMA",
    "ACRILICO", "SPANDEX", "LYCRA", "TERGAL", "NYLON",
})

MATERIAL_NORMALIZATION: dict[str, str] = {
    "ACERO_INOXIDABLE": "ACERO",
    "ACERO INOXIDABLE": "ACERO",
    "WOOD": "MADERA",
    "CORK": "CORCHO",
    "COTTON": "ALGODON",
    "LEATHER": "CUERO",
    "STEEL": "METAL",
    "ALUMINUM": "ALUMINIO",
    "ALUMINIUM": "ALUMINIO",
    "BAMBOO": "BAMBU",
    "GLASS": "VIDRIO",
    "CRYSTAL": "VIDRIO",
    "PORCELAIN": "CERAMICA",
    "CERAMIC": "CERAMICA",
    "RUBBER": "CAUCHO",
    "SILICON": "SILICONA",
    "RECYCLED": "RPET",
    "POLYESTER": "POLIESTER",
    "FIBER": "SINTETICO",
}


class CommercialRecommendationEngine:

    def recommend(self, query: StructuredSearchQuery) -> RecommendationOutput:
        output = RecommendationOutput(
            query=query.original_query,
            audience=query.detected_audience,
            category=query.detected_categories[0] if query.detected_categories else None,
            price_intent=query.detected_price_intent,
            quality_intent=query.detected_quality_intent,
            eco_intent=query.detected_eco_intent,
            technologies=query.detected_technologies or [],
        )

        reasons: list[str] = []

        if query.detected_audience:
            rules = get_audience_rules(query.detected_audience)
            if rules:
                self._extend(output.preferred_product_families, rules.get("preferred_families", []))
                self._extend(output.preferred_categories, rules.get("preferred_categories", []))
                self._extend(output.preferred_materials, rules.get("preferred_materials", []))
                self._extend(output.preferred_attributes, rules.get("preferred_attributes", []))
                self._extend(output.avoid_product_families, rules.get("avoid_families", []))
                self._extend(output.avoid_categories, rules.get("avoid_categories", []))
                self._extend(output.use_cases, rules.get("use_cases", []))
                reasons.append(f"reglas_audiencia:{query.detected_audience}")

        if query.detected_categories:
            for cat in query.detected_categories:
                rules = get_category_rules(cat)
                if rules:
                    self._extend(output.preferred_product_families, rules.get("preferred_families", []))
                    self._extend(output.preferred_technologies, rules.get("preferred_technologies", []))
                    self._extend(output.preferred_attributes, rules.get("preferred_attributes", []))
                    self._extend(output.preferred_materials, rules.get("preferred_materials", []))
                    self._extend(output.use_cases, rules.get("use_cases", []))
                    reasons.append(f"reglas_categoria:{cat}")

        if query.detected_technologies:
            for tech in query.detected_technologies:
                rules = get_technology_rules(tech)
                if rules:
                    self._extend(output.preferred_product_families, rules.get("preferred_families", []))
                    self._extend(output.preferred_attributes, rules.get("preferred_attributes", []))
                    self._extend(output.use_cases, rules.get("use_cases", []))
                    reasons.append(f"reglas_tecnologia:{tech}")

        if query.detected_price_intent:
            rules = get_price_rules(query.detected_price_intent)
            if rules:
                self._extend(output.preferred_product_families, rules.get("preferred_families", []))
                self._extend(output.preferred_materials, rules.get("preferred_materials", []))
                self._extend(output.preferred_attributes, rules.get("preferred_attributes", []))
                self._extend(output.use_cases, rules.get("use_cases", []))
                reasons.append(f"reglas_precio:{query.detected_price_intent}")

        if query.detected_quality_intent:
            rules = get_quality_rules(query.detected_quality_intent)
            if rules:
                self._extend(output.preferred_product_families, rules.get("preferred_families", []))
                self._extend(output.preferred_materials, rules.get("preferred_materials", []))
                self._extend(output.preferred_attributes, rules.get("preferred_attributes", []))
                self._extend(output.use_cases, rules.get("use_cases", []))
                reasons.append(f"reglas_calidad:{query.detected_quality_intent}")

        if query.detected_eco_intent:
            eco_rules = get_category_rules("Eco")
            if eco_rules:
                self._extend(output.preferred_product_families, eco_rules.get("preferred_families", []))
                self._extend(output.preferred_materials, eco_rules.get("preferred_materials", []))
                self._extend(output.preferred_attributes, eco_rules.get("preferred_attributes", []))
                self._extend(output.use_cases, eco_rules.get("use_cases", []))
                reasons.append("reglas_eco")

        is_eco_context = (
            query.detected_eco_intent
            or any(c.lower() == "eco" for c in (query.detected_categories or []))
        )

        self._resolve(output, is_eco_context)
        output.reason = " | ".join(reasons) if reasons else "sin_reglas_comerciales"
        return output

    def _extend(self, target: list[str], items: list[str]) -> None:
        for item in items:
            if item not in target:
                target.append(item)

    def _resolve(self, output: RecommendationOutput, is_eco_context: bool) -> None:
        # Conflicto 1: preferred families - avoid families
        avoid_set = set(output.avoid_product_families)
        output.preferred_product_families = [
            f for f in output.preferred_product_families if f not in avoid_set
        ]

        # Conflicto 2: remove non-eco materials in eco context
        if is_eco_context:
            output.preferred_materials = [
                m for m in output.preferred_materials
                if m not in NON_ECO_MATERIALS
            ]

        # Conflicto 3: normalize material names
        output.preferred_materials = [
            MATERIAL_NORMALIZATION.get(m, m) for m in output.preferred_materials
        ]

        # Conflicto 4: deduplicate preserving order
        output.preferred_product_families = self._dedup(output.preferred_product_families)
        output.preferred_categories = self._dedup(output.preferred_categories)
        output.preferred_materials = self._dedup(output.preferred_materials)
        output.preferred_attributes = self._dedup(output.preferred_attributes)
        output.preferred_technologies = self._dedup(output.preferred_technologies)
        output.avoid_product_families = self._dedup(output.avoid_product_families)
        output.avoid_categories = self._dedup(output.avoid_categories)
        output.use_cases = self._dedup(output.use_cases)

    def _dedup(self, items: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
