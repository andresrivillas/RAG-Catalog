from ..enrichment.product_html_parser import SCRAPER_DENYLIST, ScrapedProduct
from ...domain.entities.product_knowledge import ProductKnowledge


EXCEL_CONFIDENCE = 0.9
SCRAPER_CONFIDENCE = 0.7
TAINTED_CONFIDENCE = 0.3


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

        # Datos estructurados del scraper.
        if scraped.availability is not None:
            product.availability = scraped.availability
        if scraped.breadcrumb:
            product.breadcrumb = scraped.breadcrumb

        return product

    def _best(self, current: str, scraped: str) -> str:
        current = (current or "").strip()
        scraped = (scraped or "").strip()

        if not scraped:
            return current

        current_conf = EXCEL_CONFIDENCE if current else 0.0
        scraped_conf = SCRAPER_CONFIDENCE
        if self._contains_denylist(scraped):
            scraped_conf = TAINTED_CONFIDENCE

        clean_scraped = self._clean_scraped(scraped)
        is_scraped_noise = not clean_scraped

        if not current:
            # Usar el scraped si tiene algún contenido limpio, aunque esté manchado.
            return scraped if not is_scraped_noise else current

        if is_scraped_noise:
            return current

        if scraped_conf > current_conf:
            return scraped
        if current_conf > scraped_conf:
            return current
        # Empate: preferir el texto limpio más corto.
        clean_current = self._clean_scraped(current)
        if len(clean_scraped) < len(clean_current):
            return scraped
        return current

    @staticmethod
    def _contains_denylist(text: str) -> bool:
        lower = text.lower()
        return any(deny in lower for deny in SCRAPER_DENYLIST)

    @staticmethod
    def _clean_scraped(text: str) -> str:
        """Devuelve el contenido limpio del texto eliminando fragmentos con términos
        no deseados. Se usa para decidir si el scraped aporta valor real.
        """
        if not text:
            return ""
        fragments = [f.strip() for f in text.replace("\r", "\n").split("\n") if f.strip()]
        if not fragments:
            import re

            fragments = [
                s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()
            ]
        clean = []
        for fragment in fragments:
            lower = fragment.lower()
            if any(deny in lower for deny in SCRAPER_DENYLIST):
                continue
            clean.append(fragment)
        return " ".join(" ".join(clean).split())
