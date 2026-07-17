from typing import Optional

from .models import Evidence
from .signals import (
    SIGNAL_MATERIAL_PREMIUM, SIGNAL_MATERIAL_ECO, SIGNAL_MATERIAL_TECH,
    SIGNAL_MATERIAL_LUXURY, SIGNAL_MATERIAL_EXECUTIVE,
    SIGNAL_NAME_PREMIUM, SIGNAL_NAME_ECO, SIGNAL_NAME_TECH,
    SIGNAL_NAME_EXECUTIVE, SIGNAL_NAME_LUXURY, SIGNAL_NAME_INNOVATION,
    SIGNAL_NAME_INDUSTRY, SIGNAL_NAME_CUSTOMER,
    SIGNAL_NAME_OCCASION, SIGNAL_NAME_CAMPAIGN,
    SIGNAL_TAG_PREMIUM, SIGNAL_TAG_ECO, SIGNAL_TAG_TECH,
    SIGNAL_TAG_EXECUTIVE, SIGNAL_TAG_INDUSTRY,
    SIGNAL_CATEGORY_INDUSTRY,
    DIFFERENTIATOR_KEYWORDS,
)
from ..shared.product_family_dictionary import PRODUCT_FAMILIES


def _name_lower(product: dict) -> str:
    return (product.get("name") or "").lower()


def _description_lower(product: dict) -> str:
    return (product.get("description") or "").lower()


def _material_lower(product: dict) -> str:
    return (product.get("materials") or "").lower()


def _commercial_tags(product: dict) -> list[str]:
    tags = product.get("commercial_tags") or []
    if isinstance(tags, str):
        return [t.strip().lower() for t in tags.split(",") if t.strip()]
    return [t.lower() for t in tags if t]


def _category_lower(product: dict) -> str:
    return (product.get("category") or "").lower()


def _subcategory_lower(product: dict) -> str:
    return (product.get("subcategory") or "").lower()


def _keywords(product: dict) -> list[str]:
    kw = product.get("keywords") or []
    return [k.lower() for k in kw]


def extract_material_evidence(product: dict) -> list[Evidence]:
    results: list[Evidence] = []
    mat = _material_lower(product)
    if not mat:
        return results
    for mat_part in mat.split(","):
        mp = mat_part.strip()
        for mat_type, signal_map in [
            ("premium", SIGNAL_MATERIAL_PREMIUM),
            ("eco", SIGNAL_MATERIAL_ECO),
            ("tech", SIGNAL_MATERIAL_TECH),
            ("luxury", SIGNAL_MATERIAL_LUXURY),
            ("executive", SIGNAL_MATERIAL_EXECUTIVE),
        ]:
            for key, weight in signal_map.items():
                if key in mp:
                    results.append(Evidence(
                        source=f"material_{mat_type}",
                        value=mp,
                        weight=weight,
                    ))
                    break
    return results


def extract_name_evidence(product: dict) -> list[Evidence]:
    results: list[Evidence] = []
    name = _name_lower(product)
    if not name:
        return results
    for name_type, signal_map in [
        ("premium", SIGNAL_NAME_PREMIUM),
        ("eco", SIGNAL_NAME_ECO),
        ("tech", SIGNAL_NAME_TECH),
        ("executive", SIGNAL_NAME_EXECUTIVE),
        ("luxury", SIGNAL_NAME_LUXURY),
        ("innovation", SIGNAL_NAME_INNOVATION),
    ]:
        for keyword, weight in signal_map.items():
            if keyword in name:
                results.append(Evidence(
                    source=f"name_{name_type}",
                    value=keyword,
                    weight=weight,
                ))
    for keyword, industries in SIGNAL_NAME_INDUSTRY.items():
        if keyword in name:
            for ind, weight in industries.items():
                results.append(Evidence(
                    source="name_industry",
                    value=ind,
                    weight=weight,
                ))
    for keyword, customers in SIGNAL_NAME_CUSTOMER.items():
        if keyword in name:
            for cust, weight in customers.items():
                results.append(Evidence(
                    source="name_customer",
                    value=cust,
                    weight=weight,
                ))
    for keyword, occasions in SIGNAL_NAME_OCCASION.items():
        if keyword in name:
            for occ, weight in occasions.items():
                results.append(Evidence(
                    source="name_occasion",
                    value=occ,
                    weight=weight,
                ))
    for keyword, campaigns in SIGNAL_NAME_CAMPAIGN.items():
        if keyword in name:
            for camp, weight in campaigns.items():
                results.append(Evidence(
                    source="name_campaign",
                    value=camp,
                    weight=weight,
                ))
    return results


def extract_tag_evidence(product: dict) -> list[Evidence]:
    results: list[Evidence] = []
    tags = _commercial_tags(product)
    if not tags:
        return results
    for tag_type, signal_map in [
        ("premium", SIGNAL_TAG_PREMIUM),
        ("eco", SIGNAL_TAG_ECO),
        ("tech", SIGNAL_TAG_TECH),
        ("executive", SIGNAL_TAG_EXECUTIVE),
    ]:
        for keyword, weight in signal_map.items():
            if keyword in tags:
                results.append(Evidence(
                    source=f"tag_{tag_type}",
                    value=keyword,
                    weight=weight,
                ))
    for tag, industries in SIGNAL_TAG_INDUSTRY.items():
        if tag in tags:
            for ind, weight in industries.items():
                results.append(Evidence(
                    source="tag_industry",
                    value=ind,
                    weight=weight,
                ))
    return results


def extract_category_evidence(product: dict) -> list[Evidence]:
    results: list[Evidence] = []
    cat = _category_lower(product)
    if not cat:
        return results
    for keyword, industries in SIGNAL_CATEGORY_INDUSTRY.items():
        if keyword in cat:
            for ind, weight in industries.items():
                results.append(Evidence(
                    source="category_industry",
                    value=ind,
                    weight=weight,
                ))
    return results


def extract_price_evidence(product: dict) -> list[Evidence]:
    results: list[Evidence] = []
    price = product.get("price", 0) or 0
    if price >= 80000:
        results.append(Evidence(source="price_high", value="precio_alto", weight=0.35))
    elif price >= 40000:
        results.append(Evidence(source="price_medium_high", value="precio_medio_alto", weight=0.20))
    elif price >= 15000:
        results.append(Evidence(source="price_medium", value="precio_medio", weight=0.08))
    elif price <= 5000:
        results.append(Evidence(source="price_low", value="precio_bajo", weight=0.15))
    return results


def extract_perceived_value_evidence(product: dict) -> list[Evidence]:
    results: list[Evidence] = []
    pvl = (product.get("perceived_value_level") or "").lower()
    if pvl == "alto":
        results.append(Evidence(source="perceived_value", value="alto", weight=0.30))
    elif pvl == "medio":
        results.append(Evidence(source="perceived_value", value="medio", weight=0.05))
    return results


def extract_eco_flag_evidence(product: dict) -> list[Evidence]:
    results: list[Evidence] = []
    mat = _material_lower(product)
    cat = _category_lower(product)
    name = _name_lower(product)
    if "eco" in mat or "eco" in cat or "eco" in name:
        results.append(Evidence(source="eco_reference", value="eco_referencia", weight=0.15))
    return results


def extract_differentiators(product: dict) -> list[str]:
    results: list[str] = []
    name = _name_lower(product)
    desc = _description_lower(product)
    combined = f"{name} {desc}"
    for diff, keywords in DIFFERENTIATOR_KEYWORDS.items():
        for kw in keywords:
            if kw in combined:
                results.append(diff)
                break
    return results


def extract_family(product: dict) -> Optional[str]:
    name = _name_lower(product)
    cat = _category_lower(product)
    for key, family in PRODUCT_FAMILIES.items():
        for term in family["name_terms"]:
            if term.lower() in name:
                return key
    for key, family in PRODUCT_FAMILIES.items():
        for pt in family["product_types"]:
            if pt.lower() in name or pt.lower() in cat:
                return key
    return None


def extract_all_evidence(product: dict) -> dict:
    return {
        "material": extract_material_evidence(product),
        "name": extract_name_evidence(product),
        "tag": extract_tag_evidence(product),
        "category": extract_category_evidence(product),
        "price": extract_price_evidence(product),
        "perceived_value": extract_perceived_value_evidence(product),
        "eco_flag": extract_eco_flag_evidence(product),
    }
