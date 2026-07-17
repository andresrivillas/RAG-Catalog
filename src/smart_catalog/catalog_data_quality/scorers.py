from typing import Optional

from .models import CatalogQuality, DetectedProblem, classify_score
from .validators import (
    validate_field_exists, validate_materials, validate_category,
    find_missing_fields, suggest_priority_fields,
    GENERIC_CATEGORIES,
)


def _count_known_fields(product: dict) -> int:
    fields = ["name", "category", "subcategory", "materials", "description",
               "colors", "characteristics", "price", "benefits"]
    return sum(1 for f in fields if validate_field_exists(product, f))


TOTAL_FIELDS = 9


def compute_completeness(product: dict) -> float:
    known = _count_known_fields(product)
    score = known / TOTAL_FIELDS
    return round(min(1.0, score), 4)


def compute_metadata(product: dict) -> float:
    score = 0.0
    if validate_field_exists(product, "materials"):
        score += 0.25
    if validate_field_exists(product, "colors"):
        score += 0.15
    if validate_field_exists(product, "description"):
        score += 0.25
    if validate_field_exists(product, "commercial_tags"):
        score += 0.20
    if validate_field_exists(product, "occasion_tags"):
        score += 0.10
    if validate_field_exists(product, "audience_tags"):
        score += 0.05
    return round(min(1.0, score), 4)


def compute_classification(product: dict) -> float:
    score = 0.5
    cat = (product.get("category") or "").strip()

    if not cat:
        return 0.0
    if cat.lower() in GENERIC_CATEGORIES:
        return 0.2

    has_sub = validate_field_exists(product, "subcategory")
    if has_sub:
        score += 0.2

    has_commercial_tags = validate_field_exists(product, "commercial_tags")
    if has_commercial_tags:
        score += 0.15

    price = product.get("price", 0)
    if price and price > 0:
        score += 0.15

    return round(min(1.0, score), 4)


def compute_searchability(product: dict) -> float:
    score = 0.3
    name = (product.get("name") or "").strip()
    if len(name) > 10:
        score += 0.15
    if " " in name:
        score += 0.10
    if validate_field_exists(product, "description"):
        score += 0.20
    if validate_field_exists(product, "keywords"):
        kw = product.get("keywords", [])
        if kw and len(kw) > 1:
            score += 0.15
    if validate_field_exists(product, "commercial_tags"):
        score += 0.10
    return round(min(1.0, score), 4)


def compute_evidence(
    product: dict,
    enrichment_confidence: Optional[float],
) -> float:
    score = 0.0
    if enrichment_confidence:
        score += enrichment_confidence * 0.5
    has_mats, valid_mats = validate_materials(product)
    if has_mats and valid_mats:
        score += 0.2
    if validate_field_exists(product, "commercial_tags"):
        score += 0.15
    if validate_field_exists(product, "description"):
        score += 0.15
    return round(min(1.0, score), 4)


def compute_data_quality_score(
    completeness: float,
    metadata: float,
    commercial: float,
    classification: float,
    searchability: float,
    evidence: float,
) -> float:
    score = (
        completeness * 0.25
        + metadata * 0.20
        + commercial * 0.20
        + classification * 0.15
        + searchability * 0.10
        + evidence * 0.10
    )
    return round(min(1.0, score), 4)


def compute_improvement_priority(
    quality: CatalogQuality,
    search_frequency: float = 0.0,
) -> float:
    base = 1.0 - quality.data_quality_score
    missing_penalty = len(quality.missing_fields) / 10.0
    generic_penalty = 0.2 if quality.category_is_generic else 0.0
    has_commercial = 0.15 if quality.has_commercial_knowledge_strong else 0.0
    has_mats = 0.10 if quality.has_materials else 0.0

    priority = (
        base * 0.40
        + missing_penalty * 0.20
        + generic_penalty * 0.10
        + search_frequency * 0.15
        + (1.0 - has_commercial) * 0.10
        + (1.0 - has_mats) * 0.05
    )
    return round(min(1.0, priority), 4)


def assess_product(
    product: dict,
    enrichment_confidence: Optional[float] = None,
    has_family: bool = False,
    has_commercial_strong: bool = False,
    search_frequency: float = 0.0,
) -> CatalogQuality:
    ref = product.get("reference", "")
    name = product.get("name", "")

    completeness = compute_completeness(product)
    metadata = compute_metadata(product)
    classification = compute_classification(product)
    searchability = compute_searchability(product)
    evidence = compute_evidence(product, enrichment_confidence)

    commercial = round((has_commercial_strong * 0.7 + evidence * 0.3), 4)

    dq_score = compute_data_quality_score(
        completeness, metadata, commercial, classification, searchability, evidence,
    )

    level = classify_score(dq_score)
    missing = find_missing_fields(product)
    suggested = suggest_priority_fields(product)
    problems: list[DetectedProblem] = []
    has_mats, _ = validate_materials(product)
    _, is_generic, _ = validate_category(product)
    has_desc = validate_field_exists(product, "description")
    has_tags = validate_field_exists(product, "commercial_tags")
    has_colors = validate_field_exists(product, "colors")

    quality = CatalogQuality(
        product_reference=ref,
        product_name=name,
        data_quality_score=dq_score,
        completeness_score=completeness,
        metadata_score=metadata,
        commercial_score=commercial,
        classification_score=classification,
        searchability_score=searchability,
        evidence_score=evidence,
        classification_level=level,
        missing_fields=missing,
        suggested_fields=suggested,
        has_family=has_family,
        has_materials=has_mats,
        has_description=has_desc,
        has_tags=has_tags,
        has_colors=has_colors,
        has_commercial_knowledge_strong=has_commercial_strong,
        category_is_generic=is_generic,
    )

    priority = compute_improvement_priority(quality, search_frequency)
    quality.improvement_priority = priority

    return quality
