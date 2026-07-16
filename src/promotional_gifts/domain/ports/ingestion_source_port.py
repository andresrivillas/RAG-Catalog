from abc import ABC, abstractmethod
from typing import List

from ..entities.product_knowledge import ProductKnowledge


class IngestionSourcePort(ABC):
    @abstractmethod
    def load(self) -> List[ProductKnowledge]:
        raise NotImplementedError
