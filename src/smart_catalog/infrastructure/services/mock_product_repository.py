from typing import Optional

from ...domain.models.catalog_product import CatalogProduct
from ...domain.ports.product_repository import ProductRepository


class MockProductRepository(ProductRepository):
    def get_by_reference(self, reference: str) -> Optional[CatalogProduct]:
        return None

    def get_all(self) -> list[CatalogProduct]:
        return []
