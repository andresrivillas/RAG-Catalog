from ..entities.commercial_intent import CommercialIntent
from ..entities.product_knowledge import ProductKnowledge


class CommercialScorer:
    GIFT_KEYWORDS = [
        "regalo", "gift", "promocional", "souvenir", "detalle", "recuerdo",
        "premio", "obsequio",
    ]
    PREMIUM_MATERIALS = [
        "cuero", "leather", "acero", "madera", "bambu", "bambú", "aluminio",
        "vidrio", "cristal", "silicona",
    ]
    UTILITY_KEYWORDS = [
        "reusable", "plegable", "multiusos", "portatil", "portátil", "carga",
        "termo", "impermeable", "duradero",
    ]

    def score(
        self, intent: CommercialIntent, product: ProductKnowledge
    ) -> float:
        score = 0.0
        text = (
            f"{product.name} {product.description} {product.benefits} "
            f"{' '.join(product.commercial_tags)}".lower()
        )

        if any(kw in text for kw in self.GIFT_KEYWORDS):
            score += 25
        if any(t in text for t in self.PREMIUM_MATERIALS):
            score += 20
        if any(u in text for u in self.UTILITY_KEYWORDS):
            score += 15
        if "personalizable" in product.commercial_tags:
            score += 15
        if product.perceived_value_level == "alto":
            score += 15
        elif product.perceived_value_level == "medio":
            score += 8
        if len(product.benefits) >= 20:
            score += 10

        return min(score, 100.0)
