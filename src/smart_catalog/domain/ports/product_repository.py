from abc import ABC, abstractmethod
from typing import Optional

from ..models.catalog_product import CatalogProduct


class ProductRepository(ABC):
    @abstractmethod
    def get_by_reference(self, reference: str) -> Optional[CatalogProduct]:
        ...

    @abstractmethod
    def get_all(self) -> list[CatalogProduct]:
        ...
