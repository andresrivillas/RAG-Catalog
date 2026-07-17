from datetime import datetime

from .models import CatalogKnowledge, InferredAttribute
from .extractors import (
    extract_all_evidence, extract_differentiators, extract_family,
)
from .inferences import (
    infer_premium, infer_eco, infer_tech, infer_executive, infer_luxury,
    infer_innovation, infer_commercial_value, infer_corporate_affinity,
    infer_practicality, infer_price_position, infer_industries,
    infer_customers, infer_occasions, infer_campaigns,
    build_commercial_tags, compute_overall_confidence,
)
from .store import CatalogKnowledgeStore


def enrich_single_product(product: dict, all_prices: list[float]) -> CatalogKnowledge:
    evidence = extract_all_evidence(product)

    family = extract_family(product) or ""

    premium = infer_premium(evidence)
    eco = infer_eco(evidence)
    tech = infer_tech(evidence)
    executive = infer_executive(evidence)
    luxury = infer_luxury(evidence)
    innovation = infer_innovation(evidence)
    practicality = infer_practicality(evidence)
    price_pos = infer_price_position(product.get("price", 0) or 0, all_prices)
    commercial_val = infer_commercial_value(evidence, product.get("price", 0) or 0)
    corp_aff = infer_corporate_affinity(evidence)
    industries = infer_industries(evidence)
    customers = infer_customers(evidence)
    occasions = infer_occasions(evidence)
    campaigns = infer_campaigns(evidence)
    differentiators = extract_differentiators(product)
    tags = build_commercial_tags(premium, eco, tech, executive, luxury, industries)

    all_attrs = [premium, eco, tech, executive, luxury, innovation,
                 practicality, price_pos, commercial_val, corp_aff]
    overall_conf = compute_overall_confidence(all_attrs)

    return CatalogKnowledge(
        product_reference=product.get("reference", ""),
        product_family=InferredAttribute(value=family, confidence=0.5),
        premium_level=premium,
        eco_level=eco,
        technology_level=tech,
        executive_level=executive,
        luxury_level=luxury,
        innovation_level=innovation,
        practicality_level=practicality,
        price_position=price_pos,
        commercial_value=commercial_val,
        corporate_affinity=corp_aff,
        target_industries=industries,
        target_customers=customers,
        gift_occasions=occasions,
        campaign_types=campaigns,
        commercial_tags=tags,
        differentiators=differentiators,
        overall_confidence=overall_conf,
        generated_from="auto",
        generated_at=datetime.now().isoformat(),
    )


def enrich_catalog(products: list[dict], store: CatalogKnowledgeStore) -> int:
    all_prices = [p.get("price", 0) or 0 for p in products]
    enriched_count = 0
    for product in products:
        ref = product.get("reference", "")
        if not ref:
            continue
        knowledge = enrich_single_product(product, all_prices)
        store.set(ref, knowledge)
        enriched_count += 1
    store.save()
    return enriched_count
