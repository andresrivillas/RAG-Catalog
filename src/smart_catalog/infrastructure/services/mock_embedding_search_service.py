from ...domain.ports.embedding_search_service import EmbeddingSearchService


class MockEmbeddingSearchService(EmbeddingSearchService):
    def search(self, text: str, top_k: int = 20) -> list[dict]:
        return []
