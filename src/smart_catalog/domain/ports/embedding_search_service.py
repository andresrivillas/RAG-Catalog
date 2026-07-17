from abc import ABC, abstractmethod


class EmbeddingSearchService(ABC):
    @abstractmethod
    def search(self, text: str, top_k: int = 20) -> list[dict]:
        ...
