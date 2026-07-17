from abc import ABC, abstractmethod
from typing import Optional

from ..models.catalog_product import CatalogProduct


class MetadataResolver(ABC):
    @abstractmethod
    def resolve(self, product: CatalogProduct) -> dict:
        ...

    @abstractmethod
    def enrich(self, product: CatalogProduct) -> Optional[CatalogProduct]:
        ...
