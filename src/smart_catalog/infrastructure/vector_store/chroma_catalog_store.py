from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import chromadb


@dataclass
class ChromaProductHit:
    reference: str
    name: str
    price: float
    currency: str
    description: str
    category: str
    subcategory: str
    materials: str
    colors: str
    benefits: str
    perceived_value_level: str
    commercial_tags: list[str]
    occasion_tags: list[str]
    audience_tags: list[str]
    thumbnail_url: str
    detail_url: str
    score: float


class ChromaCatalogStore:
    def __init__(self, persist_directory: Path, collection_name: str) -> None:
        self.client = chromadb.PersistentClient(path=str(persist_directory))
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def search(
        self, query: str, top_k: int = 20
    ) -> list[ChromaProductHit]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["metadatas", "distances"],
        )

        hits: list[ChromaProductHit] = []
        if not results["ids"] or not results["ids"][0]:
            return hits

        for metadata, distance in zip(
            results["metadatas"][0],
            results["distances"][0],
        ):
            score = 1.0 - float(distance)
            hits.append(
                ChromaProductHit(
                    reference=metadata.get("reference", ""),
                    name=metadata.get("name", ""),
                    price=float(metadata.get("price", 0.0)),
                    currency=metadata.get("currency", "COP"),
                    description=metadata.get("description", ""),
                    category=metadata.get("category", ""),
                    subcategory=metadata.get("subcategory", ""),
                    materials=metadata.get("materials", ""),
                    colors=metadata.get("colors", ""),
                    benefits=metadata.get("benefits", ""),
                    perceived_value_level=metadata.get(
                        "perceived_value_level", "medio"
                    ),
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
                    thumbnail_url=metadata.get("thumbnail_url", ""),
                    detail_url=metadata.get("detail_url", ""),
                    score=score,
                )
            )

        return hits

    def count(self) -> int:
        return self.collection.count()
