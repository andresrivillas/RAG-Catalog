from ...domain.ports.keyword_search_service import KeywordSearchService


class MockKeywordSearchService(KeywordSearchService):
    def search(self, text: str, top_k: int = 20) -> list[dict]:
        return []
