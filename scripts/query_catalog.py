from config.settings import settings

from promotional_gifts.container import build_vector_store


def main() -> None:
    vector_store = build_vector_store()
    total = vector_store.count()
    print(f"Productos en la base de conocimiento: {total}")
    if total == 0:
        print("La base está vacía. Ejecuta primero: python scripts/index_catalog.py")
        return

    while True:
        query = input("\nConsulta (q para salir): ").strip()
        if query.lower() in ("q", "quit", "salir"):
            break
        if not query:
            continue

        results = vector_store.search(query=query, top_k=settings.top_k)
        print(f"\nTop {len(results)} resultados para: '{query}'")
        print("-" * 60)
        for product, score in results:
            print(f"Referencia : {product.reference}")
            print(f"Nombre     : {product.name}")
            print(f"Precio     : {product.price}")
            print(f"Score      : {score:.4f}")
            description = product.description or "(sin descripción)"
            print(f"Descripción: {description[:160]}")
            print("-" * 60)


if __name__ == "__main__":
    main()
