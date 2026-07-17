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
                "category": p.category,
                "materials": p.materials,
                "colors": p.colors,
                "commercial_tags": ",".join(p.commercial_tags),
                "occasion_tags": ",".join(p.occasion_tags),
                "audience_tags": ",".join(p.audience_tags),
                "perceived_value_level": p.perceived_value_level,
                "benefits": p.benefits,
                "thumbnail_url": p.thumbnail_url or p.image_url or "",
                "detail_url": p.detail_url or p.url or "",
            }
            for p in products
        ]

        # Usar upsert para permitir re-indexaciones sin duplicados ni fallos.
        self.collection.upsert(
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
                category=metadata.get("category", ""),
                materials=metadata.get("materials", ""),
                colors=metadata.get("colors", ""),
                commercial_tags=(
                    metadata.get("commercial_tags", "").split(",")
                    if metadata.get("commercial_tags")
                    else []
                ),
                occasion_tags=(
                    metadata.get("occasion_tags", "").split(",")
                    if metadata.get("occasion_tags")
                    else []
                ),
                audience_tags=(
                    metadata.get("audience_tags", "").split(",")
                    if metadata.get("audience_tags")
                    else []
                ),
                perceived_value_level=metadata.get(
                    "perceived_value_level", "medio"
                ),
                benefits=metadata.get("benefits", ""),
                thumbnail_url=metadata.get("thumbnail_url", ""),
                detail_url=metadata.get("detail_url", ""),
                url=metadata.get("detail_url", ""),
            )
            product.embedding_text = document
            score = 1.0 - float(distance)
            output.append((product, score))

        return output

    def count(self) -> int:
        return self.collection.count()
