from ..domain.models.catalog_product import CatalogProduct
from .models import CommercialKnowledge
from ..catalog_knowledge_enrichment.models import CatalogKnowledge as CK


def build_from_catalog_knowledge(ck: CK, product: CatalogProduct) -> CommercialKnowledge:
    industries = [i.value for i in ck.target_industries if i.confidence > 0.1]
    customers = [c.value for c in ck.target_customers if c.confidence > 0.1]
    occasions = [o.value for o in ck.gift_occasions if o.confidence > 0.1]
    campaigns = [c.value for c in ck.campaign_types if c.confidence > 0.1]

    pvl_map = {"alta": "alta_calidad", "media": "corporativo", "baja": "estandar"}
    corp_aff_val = pvl_map.get(ck.corporate_affinity.value, "estandar")

    exec_map = {"alto": "high", "medio": "medium", "bajo": "low"}
    premium_map = {"luxury": "luxury", "premium": "premium", "standard": "standard", "basic": "basic"}

    return CommercialKnowledge(
        product_reference=product.reference,
        product_family=ck.product_family.value,
        commercial_categories=list(set([product.category] + ck.commercial_tags)),
        industry_affinity=industries,
        customer_profiles=customers,
        executive_level=exec_map.get(ck.executive_level.value, "low"),
        premium_level=premium_map.get(ck.premium_level.value, "basic"),
        commercial_value=ck.commercial_value.value,
        gift_occasions=occasions,
        recommended_campaigns=campaigns,
        use_cases=[],
        corporate_affinity=0.8 if ck.corporate_affinity.value == "alta" else 0.5 if ck.corporate_affinity.value == "media" else 0.3,
        perceived_value=corp_aff_val,
        commercial_tags=ck.commercial_tags,
        search_boost_tags=[t for t in ck.commercial_tags if t not in ("lujo",)],
        search_penalty_tags=[],
        confidence=round(ck.overall_confidence, 2),
        reason=f"enriquecido: {ck.generated_from}",
    )
