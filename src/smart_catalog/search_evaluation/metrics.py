import math
from typing import Optional


def precision_at_k(retrieved: list[str], expected: list[str], k: int) -> float:
    if not retrieved or not expected or k == 0:
        return 0.0
    top = retrieved[:k]
    if not top:
        return 0.0
    hits = sum(1 for r in top if r in expected)
    return hits / min(k, len(top))


def recall_at_k(retrieved: list[str], expected: list[str], k: int) -> float:
    if not expected:
        return 0.0
    top = retrieved[:k]
    if not top:
        return 0.0
    hits = sum(1 for r in top if r in expected)
    return hits / len(expected)


def mrr(retrieved: list[list[str]], expected: list[list[str]]) -> float:
    total = 0.0
    count = 0
    for ret, exp in zip(retrieved, expected):
        if not exp:
            continue
        count += 1
        for idx, r in enumerate(ret):
            if r in exp:
                total += 1.0 / (idx + 1)
                break
    return total / count if count else 0.0


def ndcg(retrieved: list[str], expected: list[str], k: int) -> float:
    if not expected:
        return 0.0
    top = retrieved[:k]
    dcg = 0.0
    idcg = 0.0
    for i, r in enumerate(top):
        rel = 1.0 if r in expected else 0.0
        dcg += rel / math.log2(i + 2) if i > 0 else rel
    ideal = expected[:k]
    for i, r in enumerate(ideal):
        rel = 1.0
        idcg += rel / math.log2(i + 2) if i > 0 else rel
    return dcg / idcg if idcg > 0 else 0.0


def detector_accuracy(
    detected: list,
    expected: list,
) -> float:
    if not expected:
        return 1.0
    if not detected:
        return 0.0
    detected_set = set(detected)
    expected_set = set(expected)
    intersection = detected_set & expected_set
    return len(intersection) / len(expected_set) if expected_set else 1.0


def detector_coverage(detected: list, possible: list) -> float:
    if not possible:
        return 1.0
    if not detected:
        return 0.0
    detected_set = set(detected)
    possible_set = set(possible)
    intersection = detected_set & possible_set
    return len(intersection) / len(possible_set) if possible_set else 1.0


def has_recommendation_boost(explanations: list[str]) -> bool:
    for e in explanations:
        if "recomendada" in e.lower() or "recomendado" in e.lower():
            return True
    return False


def score_distribution(scores: list[float], buckets: Optional[list[float]] = None) -> dict[str, int]:
    if buckets is None:
        buckets = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    dist = {}
    for i in range(len(buckets) - 1):
        label = f"{buckets[i]:.1f}-{buckets[i+1]:.1f}"
        dist[label] = 0
    dist["1.0"] = 0
    for s in scores:
        for i in range(len(buckets) - 1):
            if buckets[i] <= s < buckets[i + 1]:
                label = f"{buckets[i]:.1f}-{buckets[i+1]:.1f}"
                dist[label] = dist.get(label, 0) + 1
                break
        if s >= 1.0:
            dist["1.0"] = dist.get("1.0", 0) + 1
    return dist
