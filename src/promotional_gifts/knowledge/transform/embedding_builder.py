from typing import List

from ...domain.entities.product_knowledge import ProductKnowledge
from ...domain.ports.embedding_port import EmbeddingPort


class EmbeddingBuilder:
    def __init__(self, embedding_port: EmbeddingPort) -> None:
        self.embedding_port = embedding_port

    def build(self, products: List[ProductKnowledge]) -> List[List[float]]:
        texts = [p.embedding_text for p in products]
        return self.embedding_port.embed(texts)
