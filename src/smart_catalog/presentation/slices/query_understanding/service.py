from ....domain.models.structured_search_query import StructuredSearchQuery
from .engine import QueryUnderstandingEngine


class QueryUnderstandingService:
    def __init__(self) -> None:
        self._engine = QueryUnderstandingEngine()

    def understand(self, text: str) -> StructuredSearchQuery:
        return self._engine.understand(text)
