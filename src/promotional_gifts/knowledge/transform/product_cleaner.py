from typing import List

from ...domain.entities.product_knowledge import ProductKnowledge


class ProductCleaner:
    def clean(self, products: List[ProductKnowledge]) -> List[ProductKnowledge]:
        cleaned: List[ProductKnowledge] = []
        seen_refs = set()

        for product in products:
            if not product.reference or product.reference in seen_refs:
                continue
            seen_refs.add(product.reference)

            product.name = self._normalize_text(product.name)
            product.characteristics = self._normalize_text(product.characteristics)
            product.description = self._normalize_text(product.description)
            product.price_description = self._normalize_text(
                product.price_description
            )
            product.additional_prices = self._normalize_text(
                product.additional_prices
            )
            if product.price.amount < 0:
                product.price = product.price.__class__(amount=0.0)

            cleaned.append(product)

        return cleaned

    def _normalize_text(self, value: str) -> str:
        if not value or value.lower() == "nan":
            return ""
        return " ".join(value.split())
