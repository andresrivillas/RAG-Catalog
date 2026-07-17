import json
import logging

from promotional_gifts.container import (
    build_enrichment_pipeline,
    build_ingestion_source,
    build_knowledge_indexer,
    settings,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def load_enriched() -> list:
    if settings.enriched_path.exists():
        with open(settings.enriched_path, encoding="utf-8") as fh:
            return json.load(fh)
    return []


def main() -> None:
    indexer = build_knowledge_indexer()

    enriched_data = load_enriched()
    if enriched_data:
        logging.info(
            "Cargando %s productos enriquecidos desde %s",
            len(enriched_data),
            settings.enriched_path,
        )
        products = indexer.load_from_dicts(enriched_data)
    else:
        logging.info("Cargando catálogo desde Excel...")
        ingestion = build_ingestion_source()
        products = ingestion.load()
        logging.info("Filas cargadas: %s", len(products))

        products = indexer.cleaner.clean(products)

        logging.info("Enriqueciendo catálogo vía web...")
        pipeline = build_enrichment_pipeline()
        products = pipeline.enrich(products)

    logging.info("Sanitizando, generando metadata y embeddings, indexando en ChromaDB...")
    products = indexer.index(products)

    # Persistir el catálogo enriquecido y sanitizado para que las próximas
    # cargas sean rápidas y consistentes con el vector store.
    sanitized_data = [
        {
            "reference": p.reference,
            "name": p.name,
            "price": p.price.amount,
            "currency": p.price.currency,
            "characteristics": p.characteristics,
            "description": p.description,
            "price_description": p.price_description,
            "additional_prices": p.additional_prices,
            "url": p.url,
            "detail_url": p.detail_url,
            "slug": p.slug,
            "image_url": p.image_url,
            "thumbnail_url": p.thumbnail_url,
            "image_urls": p.image_urls,
            "images": p.images,
            "benefits": p.benefits,
            "materials": p.materials,
            "dimensions": p.dimensions,
            "capacity": p.capacity,
            "colors": p.colors,
            "category": p.category,
            "subcategory": p.subcategory,
            "excel_category": p.excel_category,
            "recommendations": p.recommendations,
            "customization": p.customization,
            "keywords": p.keywords,
            "occasion_tags": p.occasion_tags,
            "audience_tags": p.audience_tags,
            "commercial_tags": p.commercial_tags,
            "perceived_value_level": p.perceived_value_level,
            "enriched": p.enriched,
            "availability": p.availability,
            "breadcrumb": p.breadcrumb,
        }
        for p in products
    ]
    with open(settings.enriched_path, "w", encoding="utf-8") as fh:
        json.dump(sanitized_data, fh, ensure_ascii=False, indent=2)

    logging.info("Productos indexados: %s", len(products))


if __name__ == "__main__":
    main()
