from typing import List

from ..entities.product_knowledge import ProductKnowledge


class PerceivedValueEstimator:
    PREMIUM_MATERIALS = [
        "cuero", "leather", "acero", "metal", "madera", "bambu", "bambú",
        "aluminio", "vidrio", "cristal", "silicona", "premium",
    ]
    UTILITY_KEYWORDS = [
        "reusable", "plegable", "multiusos", "portatil", "portátil", "carga",
        "usb", "inalambrico", "inalámbrico", "termost", "termo", "impermeable",
    ]

    def estimate(
        self, product: ProductKnowledge, price_median: float
    ) -> str:
        score = 0

        if product.price.amount >= price_median * 1.5:
            score += 2
        elif product.price.amount >= price_median:
            score += 1

        text = f"{product.name} {product.description} {product.characteristics}".lower()
        if any(m in text for m in self.PREMIUM_MATERIALS):
            score += 2
        if any(u in text for u in self.UTILITY_KEYWORDS):
            score += 1

        benefits = self._count_benefits(product)
        if benefits >= 3:
            score += 2
        elif benefits >= 1:
            score += 1

        if score >= 5:
            return "alto"
        if score >= 3:
            return "medio"
        return "bajo"

    def _count_benefits(self, product: ProductKnowledge) -> int:
        text = f"{product.description} {product.characteristics}".strip()
        if not text:
            return 0
        segments = [s for s in text.replace(".", ".").split(".") if len(s.strip()) > 5]
        return len(segments)
