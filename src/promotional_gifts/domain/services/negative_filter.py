from typing import List

from ..entities.product_knowledge import ProductKnowledge


class NegativeFilter:
    def __init__(self, negative_keywords: List[str]) -> None:
        self.negative_keywords = [k.lower() for k in negative_keywords]

    def is_excluded(self, product: ProductKnowledge) -> bool:
        text = (
            f"{product.category} {product.name} {product.description} "
            f"{' '.join(product.commercial_tags)} {product.materials}".lower()
        )
        return any(kw in text for kw in self.negative_keywords)
