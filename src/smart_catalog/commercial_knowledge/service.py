import logging
import time
from typing import Optional

from ..domain.models.catalog_product import CatalogProduct
from ..domain.models.catalog_search_result import CatalogSearchResult
from ..domain.models.search_explanation import SearchExplanation
from ..domain.models.search_intent import SearchIntent
from ..domain.models.search_response import SearchResponse
from ..domain.models.structured_search_query import StructuredSearchQuery
from .models import CommercialKnowledge
from .ports import CatalogKnowledgeRepository
from .rules import build_from_catalog_knowledge
from .affinity_calculator import CommercialAffinityCalculator

logger = logging.getLogger("smart_catalog.commercial_knowledge")


class CommercialKnowledgeService:
    def __init__(
        self,
        affinity_calculator: Optional[CommercialAffinityCalculator] = None,
        enrichment_store: Optional[CatalogKnowledgeRepository] = None,
    ) -> None:
        self._calculator = affinity_calculator or CommercialAffinityCalculator()
        self._cache: dict[str, CommercialKnowledge] = {}
        self._store = enrichment_store

    def get_knowledge(self, product: CatalogProduct) -> CommercialKnowledge:
        if product.reference in self._cache:
            return self._cache[product.reference]

        knowledge = CommercialKnowledge(reason="sin_conocimiento")
        if self._store is not None:
            ck = self._store.get(product.reference)
            if ck is not None:
                knowledge = build_from_catalog_knowledge(ck, product)
        self._cache[product.reference] = knowledge
        return knowledge

    def enhance(self, response: SearchResponse, structured: StructuredSearchQuery,
                intent: Optional[SearchIntent]) -> SearchResponse:
        start = time.perf_counter()

        q = structured.original_query
        logger.info("Enriqueciendo resultados para: '%s' (%d productos)", q, len(response.results))

        alpha = self._calculator.compute_blend_alpha(structured)
        enriched: list[tuple[CatalogSearchResult, float, CommercialKnowledge]] = []

        for result in response.results:
            knowledge = self.get_knowledge(result.product)
            comp_score, reasons, factors = self._calculator.calculate(
                structured, intent, knowledge,
            )
            old_score = result.relevance_score
            combined = (1.0 - alpha) * old_score + alpha * comp_score
            enriched.append((result, combined, knowledge, comp_score, reasons, factors))

        enriched.sort(key=lambda x: x[1], reverse=True)

        for idx, (result, combined, knowledge, comp_score, reasons, factors) in enumerate(enriched):
            result.relevance_score = round(combined, 4)
            result.rank = idx + 1
            self._enrich_explanation(result, structured, knowledge, comp_score, reasons, factors)

        response.results = [e[0] for e in enriched]
        response.total_results = len(response.results)

        elapsed = (time.perf_counter() - start) * 1000
        logger.info("Enriquecimiento completado en %.1fms (alpha=%.2f)", elapsed, alpha)
        return response

    def _enrich_explanation(
        self,
        result: CatalogSearchResult,
        structured: StructuredSearchQuery,
        knowledge: CommercialKnowledge,
        comp_score: float,
        reasons: list[str],
        factors: dict[str, float],
    ) -> None:
        if not result.explanation:
            result.explanation = SearchExplanation(
                reason="Relevante para la consulta",
                summary="Relevante para la consulta",
            )

        expl = result.explanation
        existing_secondary = list(expl.secondary_reasons) if expl.secondary_reasons else []

        commercial_reasons: list[str] = []
        for r in reasons:
            cr = self._format_reason(r, knowledge)
            if cr and cr not in existing_secondary and cr not in commercial_reasons:
                commercial_reasons.append(cr)

        if commercial_reasons:
            if knowledge.premium_level in ("premium", "luxury"):
                commercial_reasons.append("Producto del segmento premium")

            total_secondary = existing_secondary + commercial_reasons
            if total_secondary:
                expl.primary_reason = total_secondary[0]
                expl.reason = total_secondary[0]
                expl.secondary_reasons = total_secondary[1:]

        summary_parts = []
        if expl.summary:
            summary_parts.append(expl.summary)
        if commercial_reasons:
            summary_parts.append(commercial_reasons[0][:60])
        if summary_parts:
            expl.summary = " | ".join(summary_parts)[:120]

        matched = list(expl.matched_attributes) if expl.matched_attributes else []
        for t in knowledge.commercial_tags:
            if t not in matched:
                matched.append(t)
        expl.matched_attributes = matched

    def _format_reason(self, reason: str, knowledge: CommercialKnowledge) -> str:
        reason_lower = reason.lower()
        if "sector" in reason_lower or "industria" in reason_lower:
            return reason
        if "segmento premium" in reason_lower or "premium" in reason_lower:
            if knowledge.premium_level in ("premium", "luxury"):
                return "Pertenece al segmento premium"
        if "ejecutivo" in reason_lower or "vip" in reason_lower:
            return f"Recomendado para perfil {knowledge.customer_profiles[0].lower()}" if knowledge.customer_profiles else reason
        if "ecologico" in reason_lower or "sostenible" in reason_lower:
            return "Es un producto ecologico y sostenible"
        if "económico" in reason_lower or "economico" in reason_lower or "barato" in reason_lower:
            return "Es una opcion economica y accesible"
        if "tecnologico" in reason_lower or "tecnologia" in reason_lower:
            return "Producto tecnologico recomendado"
        if "corporativo" in reason_lower or "empresa" in reason_lower:
            return "Producto con alta afinidad corporativa"
        if "cliente" in reason_lower:
            return "Adecuado como regalo para clientes"
        if "regalo" in reason_lower:
            return reason
        if "frecuente" in reason_lower or "recomendado" in reason_lower:
            return reason
        return reason
