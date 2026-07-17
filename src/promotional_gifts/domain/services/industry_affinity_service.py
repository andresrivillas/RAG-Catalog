import unicodedata
from typing import Optional

from ...domain.entities.commercial_intent import CommercialIntent
from ...domain.entities.product_knowledge import ProductKnowledge
from .industry_knowledge import IndustryKnowledge, IndustryProfile


class IndustryAffinityService:
    """Calcula de forma determinista la afinidad entre un producto y la
    industria del cliente. No usa LLM ni embeddings.

    El score es 0..1, donde 0.5 es neutral. Se define completamente por
    los perfiles configurables en IndustryKnowledge.
    """

    def __init__(self, industry_knowledge: IndustryKnowledge = None) -> None:
        self.industry_knowledge = industry_knowledge or IndustryKnowledge()

    def affinity(
        self,
        product: ProductKnowledge,
        intent: CommercialIntent,
        role: Optional[str] = None,
    ) -> float:
        if not intent or not intent.industry:
            return 0.5
        profile = self.industry_knowledge.get(intent.industry)
        if profile is None:
            return 0.5
        return self._score(product, profile, role)

    def _score(
        self, product: ProductKnowledge, profile: IndustryProfile, role: Optional[str]
    ) -> float:
        # Base neutral: 0.5. Señal fuerte en [0, 1].
        score = 0.5
        product_category = self._ascii((product.category or "").lower())
        product_tags = {self._ascii(t.lower()) for t in (product.commercial_tags or [])}
        product_tags |= {self._ascii(t.lower()) for t in (product.audience_tags or [])}
        product_tags |= {self._ascii(t.lower()) for t in (product.occasion_tags or [])}
        product_materials = {
            self._ascii(m.lower())
            for m in (product.materials or "").replace(",", " ").replace(";", " ").split()
        }
        product_keywords = {self._ascii(k.lower()) for k in (product.keywords or [])}
        signals_text = self._ascii(
            f"{product.name} {product.description} {product.characteristics} "
            f"{product.benefits} {product.customization}"
        )
        all_signals = product_tags | product_keywords | {product_category}

        # Coincidencias positivas.
        if product_category in profile.preferred_categories:
            score += 0.45
        tag_hits = len(product_tags & profile.preferred_tags)
        if tag_hits:
            score += min(0.30, tag_hits * 0.10)
        keyword_hits = len(product_keywords & profile.preferred_tags)
        if keyword_hits:
            score += min(0.20, keyword_hits * 0.06)
        material_hits = len(product_materials & profile.preferred_materials)
        if material_hits:
            score += min(0.20, material_hits * 0.10)
        if role and role.lower() in profile.preferred_roles:
            score += 0.10

        # Conceptos comerciales (palabras preferidas en texto libre).
        concept_hits = sum(
            1 for term in profile.prefer if term in signals_text
        )
        if concept_hits:
            score += min(0.25, concept_hits * 0.08)

        # Penalizaciones por blacklist de la industria.
        if product_category in profile.blacklisted_categories:
            score -= 0.55
        blacklist_tag_hits = len(product_tags & profile.blacklisted_tags)
        if blacklist_tag_hits:
            score -= min(0.50, blacklist_tag_hits * 0.20)
        blacklist_keyword_hits = len(product_keywords & profile.blacklisted_tags)
        if blacklist_keyword_hits:
            score -= min(0.30, blacklist_keyword_hits * 0.12)
        if product_materials & profile.blacklisted_tags:
            score -= 0.15

        # Penalizacion por productos genericos rompe-kit (metros, llaveros, etc.).
        breaker_terms = {"metro", "llavero", "llaveros", "regla", "cinta metrica", "casco", "pito", "silbato", "repuesto", "adhesivo", "pegatina", "sticker", "aspiradora", "coca", "gancho", "agarradera", "balaca", "tangram", "triqui", "juego desestresante"}
        breaker_hits = sum(1 for term in breaker_terms if term in signals_text)
        if breaker_hits:
            score -= min(0.35, breaker_hits * 0.18)

        return max(0.0, min(1.0, score))

    @staticmethod
    def _ascii(text: str) -> str:
        return (
            unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        )
