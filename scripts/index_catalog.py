from promotional_gifts.container import (
    build_ingestion_source,
    build_knowledge_indexer,
)


def main() -> None:
    print("Cargando catálogo desde Excel...")
    ingestion = build_ingestion_source()
    products = ingestion.load()
    print(f"Filas cargadas: {len(products)}")

    print("Limpiando, generando texto y embeddings, indexando en ChromaDB...")
    indexer = build_knowledge_indexer()
    indexed_count = indexer.index(products)

    print(f"Productos indexados: {indexed_count}")


if __name__ == "__main__":
    main()
