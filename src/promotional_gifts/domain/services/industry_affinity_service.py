from typing import Optional

from ...domain.entities.commercial_intent import CommercialIntent
from ...domain.entities.product_knowledge import ProductKnowledge
from ..industry_knowledge import IndustryKnowledge, IndustryProfile


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
        score = 0.5
        product_category = (product.category or "").lower()
        product_tags = {t.lower() for t in (product.commercial_tags or [])}
        product_tags |= {t.lower() for t in (product.audience_tags or [])}
        product_tags |= {t.lower() for t in (product.occasion_tags or [])}
        product_materials = {m.lower() for m in (product.materials or "").replace(",", " ").replace(";", " ").split()}
        product_keywords = {k.lower() for k in (product.keywords or [])}
        all_signals = product_tags | product_keywords | {product_category}

        # Coincidencias positivas.
        if product_category in profile.preferred_categories:
            score += 0.25
        tag_hits = len(product_tags & profile.preferred_tags)
        if tag_hits:
            score += min(0.25, tag_hits * 0.08)
        keyword_hits = len(product_keywords & profile.preferred_tags)
        if keyword_hits:
            score += min(0.15, keyword_hits * 0.05)
        material_hits = len(product_materials & profile.preferred_materials)
        if material_hits:
            score += min(0.15, material_hits * 0.07)
        if role and role.lower() in profile.preferred_roles:
            score += 0.08

        # Penalizaciones por blacklist.
        if product_category in profile.blacklisted_categories:
            score -= 0.40
        blacklist_tag_hits = len(product_tags & profile.blacklisted_tags)
        if blacklist_tag_hits:
            score -= min(0.35, blacklist_tag_hits * 0.15)
        blacklist_keyword_hits = len(product_keywords & profile.blacklisted_tags)
        if blacklist_keyword_hits:
            score -= min(0.25, blacklist_keyword_hits * 0.10)
        if product_materials & profile.blacklisted_tags:
            score -= 0.10

        return max(0.0, min(1.0, score))
