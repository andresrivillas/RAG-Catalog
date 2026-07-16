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
