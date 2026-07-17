from typing import Optional
from dataclasses import dataclass, field

from ....domain.models.catalog_search_result import CatalogSearchResult
from ....domain.models.ranking_score import RankingScore
from ....domain.models.search_intent import SearchIntent
from ....domain.models.structured_search_query import StructuredSearchQuery
from ....shared.product_family_dictionary import (
    is_product_in_family,
    get_family_key,
)


@dataclass
class RankingWeights:
    semantic: float = 0.25
    material: float = 0.15
    category: float = 0.10
    price: float = 0.08
    quality: float = 0.08
    eco: float = 0.06
    audience: float = 0.02
    attribute: float = 0.04
    family: float = 0.22


ECO_MATERIALS = frozenset({
    "rpet", "bambu", "corcho", "algodon", "reciclado", "reciclable",
    "biodegradable", "yute", "lino", "cannamo", "eco",
})

PREMIUM_MATERIALS = frozenset({
    "metal", "cuero", "vidrio", "ceramica", "madera", "acero",
    "inoxidable", "aluminio", "cristal", "porcelana",
})

ECO_TAG_KEYWORDS = frozenset({
    "eco", "rpet", "reciclado", "ecologico", "sostenible",
})


class SearchRankingEngine:
    def __init__(self, weights: Optional[RankingWeights] = None) -> None:
        self._weights = weights or RankingWeights()

    def rank(
        self,
        query: StructuredSearchQuery,
        results: list[CatalogSearchResult],
        intent: Optional[SearchIntent] = None,
    ) -> list[CatalogSearchResult]:
        if not results:
            return results

        family_key = None
        if (
            intent
            and intent.intent_type == "PRODUCT_FAMILY"
            and intent.detected_product_family
        ):
            family_key = get_family_key(query.detected_product_types)

        scores = [self._compute(result, query, results, family_key) for result in results]

        max_final = max(s.final_score for s in scores) or 1.0
        min_final = min(s.final_score for s in scores)

        if max_final > min_final:
            for result, score in zip(results, scores):
                normalized = (score.final_score - min_final) / (max_final - min_final)
                result.relevance_score = round(normalized, 4)
                result.explanation.reason = score.ranking_reason if result.explanation else score.ranking_reason
        else:
            for result, score in zip(results, scores):
                result.relevance_score = score.final_score
                result.explanation.reason = score.ranking_reason if result.explanation else score.ranking_reason

        results.sort(key=lambda r: (r.relevance_score, r.product.score), reverse=True)

        for idx, result in enumerate(results):
            result.rank = idx + 1

        return results

    def _compute(
        self,
        result: CatalogSearchResult,
        query: StructuredSearchQuery,
        all_results: list[CatalogSearchResult],
        family_key: Optional[str] = None,
    ) -> RankingScore:
        product = result.product

        semantic = self._semantic_score(result)
        family = self._family_score(product, family_key)
        material = self._material_score(product, query)
        category = self._category_score(product, query)
        price = self._price_score(product, query, all_results)
        quality = self._quality_score(product, query, all_results)
        eco = self._eco_score(product, query)
        audience = self._audience_score(product, query)
        attribute = self._attribute_score(product, query)

        w = self._weights
        final = (
            w.semantic * semantic
            + w.family * family
            + w.material * material
            + w.category * category
            + w.price * price
            + w.quality * quality
            + w.eco * eco
            + w.audience * audience
            + w.attribute * attribute
        )

        reasons = []
        if family > 0.5:
            reasons.append("Coincide exactamente con la familia de productos solicitada")
        if semantic >= 0.15:
            reasons.append("Mayor similitud semantica")
        if material > 0.5:
            reasons.append("Coincide con material solicitado")
        if category > 0.5:
            reasons.append("Coincide con categoria")
        if quality > 0.5:
            reasons.append("Producto premium")
        if price > 0.5:
            reasons.append("Precio competitivo")
        if eco > 0.5:
            reasons.append("Producto ecologico")
        if attribute > 0.5:
            reasons.append("Coincide con atributos solicitados")

        return RankingScore(
            semantic_score=round(semantic, 4),
            material_score=round(material, 4),
            category_score=round(category, 4),
            price_score=round(price, 4),
            quality_score=round(quality, 4),
            eco_score=round(eco, 4),
            audience_score=round(audience, 4),
            attribute_score=round(attribute, 4),
            final_score=round(final, 4),
            ranking_reason=" | ".join(reasons[:3]) if reasons else "Orden semantico base",
        )

    def _family_score(self, product, family_key: Optional[str]) -> float:
        if not family_key:
            return 0.0
        if is_product_in_family(product.name, product.category, family_key):
            return 1.0
        return 0.0

    def _semantic_score(self, result: CatalogSearchResult) -> float:
        score = result.relevance_score
        if score <= 0:
            return 0.0
        if score >= 1.0:
            return 1.0
        return score

    def _material_score(self, product, query: StructuredSearchQuery) -> float:
        if not query.detected_materials:
            return 0.5
        product_material = product.material.lower()
        for mat in query.detected_materials:
            if mat.lower() in product_material:
                return 1.0
        return 0.0

    def _category_score(self, product, query: StructuredSearchQuery) -> float:
        if not query.detected_categories and not query.detected_product_types:
            return 0.5
        product_cat = product.category.lower()
        product_name = product.name.lower()
        for cat in query.detected_categories:
            if cat.lower() in product_cat or cat.lower() in product_name:
                return 1.0
        for pt in query.detected_product_types:
            if pt.lower() in product_cat or pt.lower() in product_name:
                return 1.0
        return 0.0

    def _price_score(self, product, query, all_results) -> float:
        intent = query.detected_price_intent
        prices = sorted(set(r.product.price for r in all_results))
        if not prices:
            return 0.5
        rank_in_prices = prices.index(product.price) if product.price in prices else 0
        position = rank_in_prices / (len(prices) - 1) if len(prices) > 1 else 0.5
        if intent == "LOW_PRICE":
            return 1.0 - position
        if intent == "HIGH_PRICE":
            return position
        return 0.5

    def _quality_score(self, product, query, all_results) -> float:
        has_intent = query.detected_quality_intent == "HIGH_QUALITY"
        if not has_intent:
            return 0.5
        score = 0.0
        material = product.material.lower()
        if product.perceived_value_level == "alto":
            score += 0.4
        if any(pm in material for pm in PREMIUM_MATERIALS):
            score += 0.3
        prices = sorted(r.product.price for r in all_results)
        if len(prices) > 1:
            position = prices.index(product.price) / (len(prices) - 1) if product.price in prices else 0.5
            if position >= 0.7:
                score += 0.3
        return min(score, 1.0)

    def _eco_score(self, product, query) -> float:
        if not query.detected_eco_intent:
            return 0.5
        if product.eco_friendly:
            return 1.0
        material = product.material.lower()
        for em in ECO_MATERIALS:
            if em in material:
                return 1.0
        for tag in product.tags:
            if tag.lower() in ECO_TAG_KEYWORDS:
                return 1.0
        return 0.0

    def _audience_score(self, product, query) -> float:
        if not query.detected_audience:
            return 0.5
        return 0.5

    def _attribute_score(self, product, query) -> float:
        matched = 0
        total = 0
        if query.detected_colors:
            total += 1
            product_colors = product.colors.lower()
            for color in query.detected_colors:
                if color.lower() in product_colors or color.lower() in product.name.lower():
                    matched += 1
                    break
        if query.detected_attributes:
            total += 1
            name_desc = f"{product.name} {product.description}".lower()
            for attr in query.detected_attributes:
                if attr.lower() in name_desc:
                    matched += 1
                    break
        if total == 0:
            return 0.5
        return matched / total
