from typing import Optional

from ....domain.models.expanded_search_query import ExpandedSearchQuery
from ....domain.models.search_intent import SearchIntent
from ....domain.models.structured_search_query import StructuredSearchQuery
from .engine import SemanticQueryExpansionEngine


class SemanticQueryExpansionService:
    def __init__(
        self,
        engine: Optional[SemanticQueryExpansionEngine] = None,
    ) -> None:
        self._engine = engine or SemanticQueryExpansionEngine()

    def expand(
        self,
        structured: StructuredSearchQuery,
        intent: Optional[SearchIntent] = None,
    ) -> ExpandedSearchQuery:
        return self._engine.expand(structured, intent)
