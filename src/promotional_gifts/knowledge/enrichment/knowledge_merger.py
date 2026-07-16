from ..enrichment.product_html_parser import ScrapedProduct
from ...domain.entities.product_knowledge import ProductKnowledge


class KnowledgeMerger:
    def merge(
        self, product: ProductKnowledge, scraped: ScrapedProduct
    ) -> ProductKnowledge:
        product.enriched = bool(
            scraped.description or scraped.materials or scraped.images
        )

        product.description = self._best(product.description, scraped.description)
        product.benefits = self._best(product.benefits, scraped.benefits)
        product.characteristics = self._best(
            product.characteristics, scraped.characteristics
        )
        product.materials = self._best(product.materials, scraped.materials)
        product.dimensions = self._best(product.dimensions, scraped.dimensions)
        product.capacity = self._best(product.capacity, scraped.capacity)
        product.colors = self._best(product.colors, scraped.colors)
        product.category = self._best(product.category, scraped.category)
        product.subcategory = self._best(
            product.subcategory, scraped.subcategory
        )
        product.recommendations = self._best(
            product.recommendations, scraped.recommendations
        )
        product.customization = self._best(
            product.customization, scraped.customization
        )

        if scraped.images:
            product.images = scraped.images
        if scraped.thumbnail_url:
            product.thumbnail_url = scraped.thumbnail_url
            product.image_url = scraped.thumbnail_url
        if scraped.image_urls:
            product.image_urls = scraped.image_urls

        product.detail_url = product.url or product.detail_url

        return product

    def _best(self, current: str, scraped: str) -> str:
        current = (current or "").strip()
        scraped = (scraped or "").strip()
        if len(scraped) > len(current):
            return scraped
        return current
