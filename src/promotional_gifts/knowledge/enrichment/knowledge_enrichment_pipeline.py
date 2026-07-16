import json
import logging
import time
from pathlib import Path
from typing import List

from .catalog_web_scraper import CatalogWebScraper
from .knowledge_merger import KnowledgeMerger
from .product_html_parser import ProductHtmlParser
from ...domain.entities.product_knowledge import ProductKnowledge

logger = logging.getLogger(__name__)


class KnowledgeEnrichmentPipeline:
    def __init__(
        self,
        scraper: CatalogWebScraper,
        parser: ProductHtmlParser,
        merger: KnowledgeMerger,
        output_path: Path,
    ) -> None:
        self.scraper = scraper
        self.parser = parser
        self.merger = merger
        self.output_path = Path(output_path)

    def enrich(self, products: List[ProductKnowledge]) -> List[ProductKnowledge]:
        start = time.time()
        processed = 0
        enriched = 0
        errors = 0

        for product in products:
            processed += 1
            try:
                html = self.scraper.fetch(product.url)
                if html:
                    scraped = self.parser.parse(html)
                    self.merger.merge(product, scraped)
                    if product.enriched:
                        enriched += 1
                else:
                    errors += 1
            except Exception as exc:  # noqa: BLE001
                errors += 1
                logger.warning(
                    "Error enriqueciendo %s: %s", product.reference, exc
                )
            if processed % 100 == 0:
                logger.info("Procesados %s/%s", processed, len(products))

        self._persist(products)
        logger.info(
            "Enriquecimiento completo: procesados=%s enriquecidos=%s errores=%s "
            "tiempo=%.1fs",
            processed,
            enriched,
            errors,
            time.time() - start,
        )
        return products

    def _persist(self, products: List[ProductKnowledge]) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        data = [self._to_dict(p) for p in products]
        self.output_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _to_dict(self, product: ProductKnowledge) -> dict:
        return {
            "reference": product.reference,
            "name": product.name,
            "price": product.price.amount,
            "currency": product.price.currency,
            "characteristics": product.characteristics,
            "description": product.description,
            "price_description": product.price_description,
            "additional_prices": product.additional_prices,
            "url": product.url,
            "benefits": product.benefits,
            "materials": product.materials,
            "dimensions": product.dimensions,
            "capacity": product.capacity,
            "colors": product.colors,
            "images": product.images,
            "category": product.category,
            "subcategory": product.subcategory,
            "recommendations": product.recommendations,
            "customization": product.customization,
            "keywords": product.keywords,
            "occasion_tags": product.occasion_tags,
            "audience_tags": product.audience_tags,
            "commercial_tags": product.commercial_tags,
            "perceived_value_level": product.perceived_value_level,
            "enriched": product.enriched,
        }
