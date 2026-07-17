from ..domain.models.catalog_product import CatalogProduct
from ..shared.product_family_dictionary import PRODUCT_FAMILIES
from .models import CommercialKnowledge
from .knowledge_base import (
    FAMILY_PROFILES,
    CATEGORY_COMMERCIAL_TAGS,
    MATERIAL_COMMERCIAL_TAGS,
    PERCEIVED_VALUE_LEVEL_MAP,
)
from ..catalog_knowledge_enrichment.models import CatalogKnowledge as CK


def build_from_catalog_knowledge(ck: CK, product: CatalogProduct) -> CommercialKnowledge:
    def _val(attr):
        return attr.value if attr else ""

    def _conf(attr):
        return attr.confidence if attr else 0.0

    def _evid_values(attr_list):
        return list(set(e.value for attr in attr_list for e in attr.evidence)) if attr_list else []

    industries = [i.value for i in ck.target_industries if i.confidence > 0.1]
    customers = [c.value for c in ck.target_customers if c.confidence > 0.1]
    occasions = [o.value for o in ck.gift_occasions if o.confidence > 0.1]
    campaigns = [c.value for c in ck.campaign_types if c.confidence > 0.1]

    pvl_map = {"alta": "alta_calidad", "media": "corporativo", "baja": "estandar"}
    corp_aff_val = pvl_map.get(ck.corporate_affinity.value, "estandar")

    premium_map = {"luxury": "luxury", "premium": "premium", "standard": "standard", "basic": "basic"}
    exec_map = {"alto": "high", "medio": "medium", "bajo": "low"}

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
        use_cases=_evid_values(ck.use_cases),
        corporate_affinity=0.8 if ck.corporate_affinity.value == "alta" else 0.5 if ck.corporate_affinity.value == "media" else 0.3,
        perceived_value=corp_aff_val,
        commercial_tags=ck.commercial_tags,
        search_boost_tags=[t for t in ck.commercial_tags if t not in ("lujo",)],
        search_penalty_tags=[],
        confidence=round(ck.overall_confidence, 2),
        reason=f"enriquecido: {ck.generated_from}",
    )


def resolve_family_key(product: CatalogProduct) -> str:
    name_lower = product.name.lower()
    for key, family in PRODUCT_FAMILIES.items():
        for term in family["name_terms"]:
            if term.lower() in name_lower:
                return key
        for ex_cat in family["exclude_categories"]:
            if ex_cat.lower() in product.category.lower():
                break
    for key, family in PRODUCT_FAMILIES.items():
        for pt in family["product_types"]:
            if pt.lower() in product.category.lower():
                return key
    return ""


def infer_category_tags(product: CatalogProduct) -> list[str]:
    cat = product.category
    for key, tags in CATEGORY_COMMERCIAL_TAGS.items():
        if key.lower() == cat.lower() or key.lower() in cat.lower():
            return tags
    for key, tags in CATEGORY_COMMERCIAL_TAGS.items():
        if any(kw in cat.lower() for kw in key.lower().split()):
            return tags
    return []


def infer_material_knowledge(product: CatalogProduct) -> dict:
    mat_lower = product.material.lower()
    for mat_key, info in MATERIAL_COMMERCIAL_TAGS.items():
        if mat_key.lower() in mat_lower:
            return info
    return {}


def infer_industry_from_category(product: CatalogProduct) -> list[str]:
    cat_lower = product.category.lower()
    industry_map = {
        "tecnologia": ["TECNOLOGIA"],
        "oficina": ["CORPORATIVO", "OFICINA"],
        "deportes": ["DEPORTES"],
        "hogar": ["HOGAR"],
        "eco": ["EDUCACION", "CONSULTORIA"],
        "textil": ["TEXTIL", "CORPORATIVO"],
        "bolsos": ["VIAJES", "CORPORATIVO"],
        "termos": ["ARQUITECTURA", "OFICINA"],
        "viaje": ["VIAJES"],
        "escritura": ["EDUCACION", "OFICINA"],
        "libretas": ["EDUCACION", "OFICINA"],
        "escolar": ["EDUCACION"],
        "bebidas": ["OFICINA", "EVENTOS"],
    }
    for keyword, industries in industry_map.items():
        if keyword in cat_lower:
            return industries
    return ["CORPORATIVO"]


def infer_executive_level(profile_tags: list[str]) -> str:
    high = ["ejecutivo", "profesional", "formal", "ejecutiva"]
    medium = ["corporativo", "oficina"]
    for h in high:
        if h in profile_tags:
            return "high"
    for m in medium:
        if m in profile_tags:
            return "medium"
    return "low"


def infer_premium_level(perceived: str, material_info: dict) -> str:
    if material_info.get("premium_level", "basic") in ("premium", "luxury"):
        return material_info["premium_level"]
    if perceived in ("alta_calidad", "alto"):
        return "premium"
    return "standard"


def infer_commercial_value(tags: list[str], price: float) -> str:
    if "premium" in tags or "lujo" in tags:
        return "high_value"
    if "ejecutivo" in tags or "profesional" in tags:
        return "valuable"
    if "economico" in tags or "promocional" in tags or price < 5000:
        return "economic"
    return "standard"


def build_knowledge(product: CatalogProduct) -> CommercialKnowledge:
    family_key = resolve_family_key(product)
    profile = FAMILY_PROFILES.get(family_key)
    material_info = infer_material_knowledge(product)
    category_tags = infer_category_tags(product)
    cat_industries = infer_industry_from_category(product)
    pvl = PERCEIVED_VALUE_LEVEL_MAP.get(product.perceived_value_level, "estandar")

    industries = list(cat_industries)
    profiles_list: list[str] = []
    occasions: list[str] = []
    campaigns: list[str] = []
    use_cases: list[str] = []
    corp_affinity = 0.3
    perceived = pvl
    comm_tags: list[str] = []
    boost: list[str] = []
    penalty: list[str] = []

    if profile:
        industries = list(set(industries + profile.industries))
        profiles_list = list(profile.customer_profiles)
        occasions = list(profile.gift_occasions)
        campaigns = list(profile.campaigns)
        use_cases = list(profile.use_cases)
        corp_affinity = max(corp_affinity, profile.corporate_affinity)
        if profile.perceived_value != "estandar":
            perceived = profile.perceived_value
        comm_tags = list(profile.commercial_tags)
        boost = list(profile.boost_tags)

    if material_info:
        mat_industries = material_info.get("industries", [])
        industries = list(set(industries + mat_industries))
        mat_tags = material_info.get("commercial_tags", [])
        comm_tags = list(set(comm_tags + mat_tags))
        perceived = material_info.get("perceived_value", perceived)

    comm_tags = list(set(comm_tags + category_tags))
    if "eco" in product.material.lower() or product.eco_friendly:
        comm_tags = list(set(comm_tags + ["ecologico", "sostenible"]))
        if "ECO" not in industries:
            industries.append("ECO")

    executive = infer_executive_level(comm_tags)
    premium = infer_premium_level(perceived, material_info)
    comval = infer_commercial_value(comm_tags, product.price)
    corp_affinity = min(1.0, corp_affinity + 0.1 * (1 if premium in ("premium", "luxury") else 0))

    reason_parts = []
    if profile:
        reason_parts.append(f"familia:{family_key}")
    if material_info:
        reason_parts.append(f"material:{product.material.split(',')[0].strip()}")
    if category_tags:
        reason_parts.append(f"categoria:{product.category}")
    reason = " | ".join(reason_parts) if reason_parts else "conocimiento generico"

    return CommercialKnowledge(
        product_reference=product.reference,
        product_family=family_key,
        commercial_categories=list(set([product.category] + comm_tags)),
        industry_affinity=industries,
        customer_profiles=profiles_list,
        executive_level=executive,
        premium_level=premium,
        commercial_value=comval,
        gift_occasions=occasions,
        recommended_campaigns=campaigns,
        use_cases=use_cases,
        corporate_affinity=round(corp_affinity, 2),
        perceived_value=perceived,
        commercial_tags=comm_tags,
        search_boost_tags=boost,
        search_penalty_tags=penalty,
        confidence=0.7 if profile else 0.4,
        reason=reason,
    )
