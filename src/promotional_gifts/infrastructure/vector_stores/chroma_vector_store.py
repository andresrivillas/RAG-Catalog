from pathlib import Path
from typing import List, Tuple

import chromadb
from chromadb.api.models.Collection import Collection

from ...domain.entities.product_knowledge import ProductKnowledge
from ...domain.ports.vector_store_port import VectorStorePort
from ...domain.value_objects.money import Money


class ChromaVectorStore(VectorStorePort):
    def __init__(
        self, persist_directory: Path, collection_name: str
    ) -> None:
        self.client = chromadb.PersistentClient(path=str(persist_directory))
        self.collection: Collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_products(self, products: List[ProductKnowledge]) -> None:
        if not products:
            return

        ids = [p.reference for p in products]
        documents = [p.embedding_text for p in products]
        metadatas = [
            {
                "reference": p.reference,
                "name": p.name,
                "price": p.price.amount,
                "currency": p.price.currency,
                "description": p.description,
            }
            for p in products
        ]

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

    def search(
        self, query: str, top_k: int
    ) -> List[Tuple[ProductKnowledge, float]]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["metadatas", "distances", "documents"],
        )

        output: List[Tuple[ProductKnowledge, float]] = []
        if not results["ids"]:
            return output

        for metadata, distance, document in zip(
            results["metadatas"][0],
            results["distances"][0],
            results["documents"][0],
        ):
            product = ProductKnowledge(
                reference=metadata["reference"],
                name=metadata["name"],
                price=Money(
                    amount=float(metadata["price"]),
                    currency=metadata.get("currency", "COP"),
                ),
                description=metadata.get("description", ""),
            )
            product.embedding_text = document
            score = 1.0 - float(distance)
            output.append((product, score))

        return output

    def count(self) -> int:
        return self.collection.count()
