from abc import ABC, abstractmethod
from typing import List, Tuple

from ..entities.product_knowledge import ProductKnowledge


class VectorStorePort(ABC):
    @abstractmethod
    def add_products(self, products: List[ProductKnowledge]) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(
        self, query: str, top_k: int
    ) -> List[Tuple[ProductKnowledge, float]]:
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        raise NotImplementedError
