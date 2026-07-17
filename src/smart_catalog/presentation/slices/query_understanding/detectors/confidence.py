from typing import Optional


def calculate_confidence(
    tokens: list[str],
    known: int,
    product_types: list[str],
    materials: list[str],
    price_intent: Optional[str],
    categories: list[str],
) -> float:
    if not tokens:
        return 0.0

    score = 0.0
    total = len(tokens)

    if total > 0:
        score += 0.40 * (known / total)

    if product_types:
        score += 0.25 * min(1.0, len(product_types))
    if materials:
        score += 0.15 * min(1.0, len(materials))
    if price_intent:
        score += 0.10
    if categories:
        score += 0.10 * min(1.0, len(categories))

    return round(min(score, 1.0), 2)
