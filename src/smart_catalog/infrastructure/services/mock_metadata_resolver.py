from typing import Optional

from ...domain.models.catalog_product import CatalogProduct
from ...domain.ports.metadata_resolver import MetadataResolver


class MockMetadataResolver(MetadataResolver):
    def resolve(self, product: CatalogProduct) -> dict:
        return {}

    def enrich(self, product: CatalogProduct) -> Optional[CatalogProduct]:
        return product
