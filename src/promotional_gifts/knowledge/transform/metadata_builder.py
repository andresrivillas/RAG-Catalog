from typing import List

from ...domain.entities.product_knowledge import ProductKnowledge


class MetadataBuilder:
    def build(self, products: List[ProductKnowledge]) -> List[ProductKnowledge]:
        for product in products:
            product.embedding_text = product.to_embedding_text()
        return products
