from typing import Optional

from .models import Evidence, InferredAttribute
from .signals import INFERRED_ATTRIBUTE_THRESHOLDS


def _sum_weights(evidence: list[Evidence], source_filter: Optional[str] = None) -> float:
    total = 0.0
    for e in evidence:
        if source_filter is None or e.source.startswith(source_filter):
            total += e.weight
    return total


def _max_evidence(evidence: list[Evidence]) -> Evidence:
    best = Evidence(weight=0.0)
    for e in evidence:
        if e.weight > best.weight:
            best = e
    return best


def _filter_evidence(evidence: list[Evidence], source_prefix: str) -> list[Evidence]:
    return [e for e in evidence if e.source.startswith(source_prefix)]


def _apply_thresholds(score: float, thresholds: list[tuple[float, str]]) -> tuple[str, float]:
    if thresholds:
        max_expected = thresholds[0][0] + 0.3
    else:
        max_expected = 1.0
    raw_confidence = min(1.0, score / max_expected) if max_expected > 0 else 0.0
    for threshold, value in thresholds:
        if score >= threshold:
            confidence = round(raw_confidence, 4)
            return value, confidence
    return thresholds[-1][1], round(raw_confidence, 4)


def infer_premium(all_evidence: dict) -> InferredAttribute:
    evidence: list[Evidence] = []
    evidence.extend(_filter_evidence(all_evidence.get("material", []), "material_premium"))
    evidence.extend(_filter_evidence(all_evidence.get("name", []), "name_premium"))
    evidence.extend(_filter_evidence(all_evidence.get("tag", []), "tag_premium"))
    for e in all_evidence.get("price", []):
        if "alto" in e.value or "medio_alto" in e.value:
            evidence.append(e)
    for e in all_evidence.get("perceived_value", []):
        if e.value == "alto":
            evidence.append(e)

    score = _sum_weights(evidence)
    value, confidence = _apply_thresholds(score, INFERRED_ATTRIBUTE_THRESHOLDS["premium_level"])
    return InferredAttribute(value=value, confidence=confidence, evidence=evidence)


def infer_eco(all_evidence: dict) -> InferredAttribute:
    evidence: list[Evidence] = []
    evidence.extend(_filter_evidence(all_evidence.get("material", []), "material_eco"))
    evidence.extend(_filter_evidence(all_evidence.get("name", []), "name_eco"))
    evidence.extend(_filter_evidence(all_evidence.get("tag", []), "tag_eco"))
    evidence.extend(all_evidence.get("eco_flag", []))

    score = _sum_weights(evidence)
    value, confidence = _apply_thresholds(score, INFERRED_ATTRIBUTE_THRESHOLDS["eco_level"])
    return InferredAttribute(value=value, confidence=confidence, evidence=evidence)


def infer_tech(all_evidence: dict) -> InferredAttribute:
    evidence: list[Evidence] = []
    evidence.extend(_filter_evidence(all_evidence.get("material", []), "material_tech"))
    evidence.extend(_filter_evidence(all_evidence.get("name", []), "name_tech"))
    evidence.extend(_filter_evidence(all_evidence.get("tag", []), "tag_tech"))

    score = _sum_weights(evidence)
    value, confidence = _apply_thresholds(score, INFERRED_ATTRIBUTE_THRESHOLDS["technology_level"])
    return InferredAttribute(value=value, confidence=confidence, evidence=evidence)


def infer_executive(all_evidence: dict) -> InferredAttribute:
    evidence: list[Evidence] = []
    evidence.extend(_filter_evidence(all_evidence.get("material", []), "material_executive"))
    evidence.extend(_filter_evidence(all_evidence.get("name", []), "name_executive"))
    evidence.extend(_filter_evidence(all_evidence.get("tag", []), "tag_executive"))
    for e in all_evidence.get("perceived_value", []):
        if e.value == "alto":
            evidence.append(Evidence(source="perceived_executive", value="alto", weight=0.10))

    score = _sum_weights(evidence)
    value, confidence = _apply_thresholds(score, INFERRED_ATTRIBUTE_THRESHOLDS["executive_level"])
    return InferredAttribute(value=value, confidence=confidence, evidence=evidence)


def infer_luxury(all_evidence: dict) -> InferredAttribute:
    evidence: list[Evidence] = []
    evidence.extend(_filter_evidence(all_evidence.get("material", []), "material_luxury"))
    evidence.extend(_filter_evidence(all_evidence.get("name", []), "name_luxury"))

    score = _sum_weights(evidence)
    value, confidence = _apply_thresholds(score, INFERRED_ATTRIBUTE_THRESHOLDS["luxury_level"])
    return InferredAttribute(value=value, confidence=confidence, evidence=evidence)


def infer_innovation(all_evidence: dict) -> InferredAttribute:
    evidence: list[Evidence] = []
    evidence.extend(_filter_evidence(all_evidence.get("name", []), "name_innovation"))

    score = _sum_weights(evidence)
    value, confidence = _apply_thresholds(score, INFERRED_ATTRIBUTE_THRESHOLDS["innovation_level"])
    return InferredAttribute(value=value, confidence=confidence, evidence=evidence)


def infer_commercial_value(all_evidence: dict, price: float) -> InferredAttribute:
    evidence: list[Evidence] = []
    premium = infer_premium(all_evidence)
    if premium.confidence > 0.2:
        evidence.append(Evidence(source="premium_value", value=premium.value, weight=0.10))
    if price >= 80000:
        evidence.append(Evidence(source="price_value", value="precio_alto", weight=0.15))
    elif price >= 40000:
        evidence.append(Evidence(source="price_value", value="precio_medio_alto", weight=0.08))
    elif price <= 5000:
        evidence.append(Evidence(source="price_value", value="precio_bajo", weight=0.10))

    score = _sum_weights(evidence)
    value, confidence = _apply_thresholds(score, INFERRED_ATTRIBUTE_THRESHOLDS["commercial_value"])
    return InferredAttribute(value=value, confidence=confidence, evidence=evidence)


def infer_corporate_affinity(all_evidence: dict) -> InferredAttribute:
    evidence: list[Evidence] = []
    for source_list in all_evidence.values():
        for e in source_list:
            if "industry" in e.source and e.value in ("CORPORATIVO", "OFICINA"):
                evidence.append(e)
    score = _sum_weights(evidence)
    value, confidence = _apply_thresholds(score, INFERRED_ATTRIBUTE_THRESHOLDS["corporate_affinity"])
    return InferredAttribute(value=value, confidence=confidence, evidence=evidence)


def infer_practicality(all_evidence: dict) -> InferredAttribute:
    evidence: list[Evidence] = []
    for e in all_evidence.get("price", []):
        if "bajo" in e.value or "medio" in e.value:
            evidence.append(Evidence(source="practical_price", value=e.value, weight=0.08))
    if _filter_evidence(all_evidence.get("material", []), "material_eco"):
        evidence.append(Evidence(source="practical_material", value="eco", weight=0.06))
    score = _sum_weights(evidence)
    value, confidence = _apply_thresholds(score, INFERRED_ATTRIBUTE_THRESHOLDS["practicality_level"])
    return InferredAttribute(value=value, confidence=confidence, evidence=evidence)


def infer_price_position(price: float, all_prices: list[float]) -> InferredAttribute:
    evidence: list[Evidence] = []
    if not all_prices:
        return InferredAttribute(value="medio", confidence=0.5)
    sorted_prices = sorted(all_prices)
    n = len(sorted_prices)
    rank = sum(1 for p in sorted_prices if p <= price)
    percentile = rank / n if n > 0 else 0.5

    if percentile >= 0.90:
        value = "muy_alto"
        evidence.append(Evidence(source="price_percentile", value="p90", weight=0.40))
    elif percentile >= 0.75:
        value = "alto"
        evidence.append(Evidence(source="price_percentile", value="p75", weight=0.30))
    elif percentile >= 0.50:
        value = "medio_alto"
        evidence.append(Evidence(source="price_percentile", value="p50", weight=0.15))
    elif percentile >= 0.25:
        value = "medio"
        evidence.append(Evidence(source="price_percentile", value="p25", weight=0.08))
    else:
        value = "bajo"
        evidence.append(Evidence(source="price_percentile", value="p10", weight=0.05))
    return InferredAttribute(value=value, confidence=round(percentile, 4), evidence=evidence)


def infer_industries(all_evidence: dict) -> list[InferredAttribute]:
    industry_scores: dict[str, list[Evidence]] = {}
    for source_list in all_evidence.values():
        for e in source_list:
            if "industry" in e.source:
                if e.value not in industry_scores:
                    industry_scores[e.value] = []
                industry_scores[e.value].append(e)

    results: list[InferredAttribute] = []
    for ind, evidence in industry_scores.items():
        score = _sum_weights(evidence)
        if score > 0.1:
            confidence = min(1.0, score / 0.5)
            results.append(InferredAttribute(value=ind, confidence=round(confidence, 4), evidence=evidence))
    results.sort(key=lambda x: x.confidence, reverse=True)
    return results


def infer_customers(all_evidence: dict) -> list[InferredAttribute]:
    customer_scores: dict[str, list[Evidence]] = {}
    for source_list in all_evidence.values():
        for e in source_list:
            if "customer" in e.source:
                if e.value not in customer_scores:
                    customer_scores[e.value] = []
                customer_scores[e.value].append(e)

    results: list[InferredAttribute] = []
    for cust, evidence in customer_scores.items():
        score = _sum_weights(evidence)
        if score > 0.1:
            confidence = min(1.0, score / 0.5)
            results.append(InferredAttribute(value=cust, confidence=round(confidence, 4), evidence=evidence))
    results.sort(key=lambda x: x.confidence, reverse=True)
    return results


def infer_occasions(all_evidence: dict) -> list[InferredAttribute]:
    occasion_scores: dict[str, list[Evidence]] = {}
    for source_list in all_evidence.values():
        for e in source_list:
            if "occasion" in e.source:
                if e.value not in occasion_scores:
                    occasion_scores[e.value] = []
                occasion_scores[e.value].append(e)
    results: list[InferredAttribute] = []
    for occ, evidence in occasion_scores.items():
        score = _sum_weights(evidence)
        if score > 0.1:
            confidence = min(1.0, score / 0.5)
            results.append(InferredAttribute(value=occ, confidence=round(confidence, 4), evidence=evidence))
    results.sort(key=lambda x: x.confidence, reverse=True)
    return results


def infer_campaigns(all_evidence: dict) -> list[InferredAttribute]:
    campaign_scores: dict[str, list[Evidence]] = {}
    for source_list in all_evidence.values():
        for e in source_list:
            if "campaign" in e.source:
                if e.value not in campaign_scores:
                    campaign_scores[e.value] = []
                campaign_scores[e.value].append(e)
    results: list[InferredAttribute] = []
    for camp, evidence in campaign_scores.items():
        score = _sum_weights(evidence)
        if score > 0.1:
            confidence = min(1.0, score / 0.5)
            results.append(InferredAttribute(value=camp, confidence=round(confidence, 4), evidence=evidence))
    results.sort(key=lambda x: x.confidence, reverse=True)
    return results


def build_commercial_tags(
    premium: InferredAttribute,
    eco: InferredAttribute,
    tech: InferredAttribute,
    executive: InferredAttribute,
    luxury: InferredAttribute,
    industries: list[InferredAttribute],
) -> list[str]:
    tags: list[str] = []
    if premium.value in ("premium", "luxury"):
        tags.append("premium")
    if eco.value in ("muy_alto", "alto"):
        tags.append("ecologico")
    if tech.value in ("muy_alto", "alto"):
        tags.append("tecnologico")
    if executive.value in ("alto", "medio"):
        tags.append("ejecutivo")
    if luxury.value in ("muy_alto", "alto"):
        tags.append("lujo")
    for ind in industries:
        tags.append(ind.value.lower())
    return list(set(tags))


def compute_overall_confidence(attributes: list[InferredAttribute]) -> float:
    if not attributes:
        return 0.0
    total = sum(a.confidence for a in attributes)
    return round(min(1.0, total / len(attributes)), 4)
