from typing import List

from ...domain.entities.product_knowledge import ProductKnowledge
from ...domain.ports.embedding_port import EmbeddingPort
from ...domain.ports.vector_store_port import VectorStorePort
from ..transform.embedding_builder import EmbeddingBuilder
from ..transform.metadata_builder import MetadataBuilder
from ..transform.product_cleaner import ProductCleaner


class KnowledgeIndexer:
    def __init__(
        self,
        cleaner: ProductCleaner,
        metadata_builder: MetadataBuilder,
        embedding_builder: EmbeddingBuilder,
        vector_store: VectorStorePort,
    ) -> None:
        self.cleaner = cleaner
        self.metadata_builder = metadata_builder
        self.embedding_builder = embedding_builder
        self.vector_store = vector_store

    def index(self, products: List[ProductKnowledge]) -> int:
        products = self.cleaner.clean(products)
        products = self.metadata_builder.build(products)
        embeddings = self.embedding_builder.build(products)
        self._attach_embeddings(products, embeddings)
        self.vector_store.add_products(products)
        return len(products)

    def _attach_embeddings(
        self, products: List[ProductKnowledge], embeddings: List[List[float]]
    ) -> None:
        for product, vector in zip(products, embeddings):
            product.embedding = vector

    def load_from_dicts(
        self, data: list
    ) -> List[ProductKnowledge]:
        from ...domain.value_objects.money import Money

        products: List[ProductKnowledge] = []
        for d in data:
            products.append(
                ProductKnowledge(
                    reference=d.get("reference", ""),
                    name=d.get("name", ""),
                    price=Money(
                        amount=float(d.get("price", 0.0)),
                        currency=d.get("currency", "COP"),
                    ),
                    characteristics=d.get("characteristics", ""),
                    description=d.get("description", ""),
                    price_description=d.get("price_description", ""),
                    additional_prices=d.get("additional_prices", ""),
                    url=d.get("url", ""),
                    benefits=d.get("benefits", ""),
                    materials=d.get("materials", ""),
                    dimensions=d.get("dimensions", ""),
                    capacity=d.get("capacity", ""),
                    colors=d.get("colors", ""),
                    images=d.get("images", []),
                    category=d.get("category", ""),
                    subcategory=d.get("subcategory", ""),
                    recommendations=d.get("recommendations", ""),
                    customization=d.get("customization", ""),
                    keywords=d.get("keywords", []),
                    occasion_tags=d.get("occasion_tags", []),
                    audience_tags=d.get("audience_tags", []),
                    commercial_tags=d.get("commercial_tags", []),
                    perceived_value_level=d.get("perceived_value_level", "medio"),
                    enriched=d.get("enriched", False),
                )
            )
        return products
