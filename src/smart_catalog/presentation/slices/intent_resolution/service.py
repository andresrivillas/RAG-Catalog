from typing import Optional

from ....domain.models.search_intent import SearchIntent
from ....domain.models.structured_search_query import StructuredSearchQuery
from .engine import IntentResolutionEngine


class IntentResolutionService:
    def __init__(
        self,
        engine: Optional[IntentResolutionEngine] = None,
    ) -> None:
        self._engine = engine or IntentResolutionEngine()

    def resolve(self, structured: StructuredSearchQuery) -> SearchIntent:
        return self._engine.resolve(structured)
