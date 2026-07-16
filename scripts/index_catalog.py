import json
import logging

from promotional_gifts.container import (
    build_enrichment_pipeline,
    build_ingestion_source,
    build_knowledge_indexer,
    build_cleaner,
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
    cleaner = build_cleaner()

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

        products = cleaner.clean(products)

        logging.info("Enriqueciendo catálogo vía web...")
        pipeline = build_enrichment_pipeline()
        products = pipeline.enrich(products)

        logging.info("Generando metadata y embeddings, indexando en ChromaDB...")
        products = indexer.metadata_builder.build(products)

    embeddings = indexer.embedding_builder.build(products)
    indexer._attach_embeddings(products, embeddings)
    indexer.vector_store.add_products(products)

    logging.info("Productos indexados: %s", len(products))


if __name__ == "__main__":
    main()
