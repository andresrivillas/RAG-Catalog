import logging
import time
from typing import Optional

from ....domain.models.expanded_search_query import ExpandedSearchQuery
from ....domain.models.search_response import SearchResponse
from ....domain.models.search_session import SearchSession
from ....domain.models.structured_search_query import StructuredSearchQuery
from .engine import ConversationContextEngine
from .session_manager import SessionManager

logger = logging.getLogger("smart_catalog.context")


class ConversationContextService:
    def __init__(
        self,
        engine: Optional[ConversationContextEngine] = None,
        session_manager: Optional[SessionManager] = None,
    ) -> None:
        self._engine = engine or ConversationContextEngine()
        self._session_manager = session_manager or SessionManager()

    def resolve(
        self,
        new_query: str,
        session: Optional[SearchSession],
    ) -> tuple[str, Optional[SearchSession]]:
        start = time.perf_counter()

        if session is None:
            session = self._session_manager.create_session()

        previous = session.current_query if session.current_query else None
        resolved = self._engine.resolve_query(new_query, previous)

        elapsed = (time.perf_counter() - start) * 1000
        relative = self._engine.is_relative(new_query)

        logger.info(
            "Contexto: entrada='%s' | anterior='%s' | resuelto='%s' | relativo=%s | tiempo=%.1fms",
            new_query, previous or "", resolved, relative, elapsed,
        )

        return resolved, session

    def update_session(
        self,
        session: SearchSession,
        query: str,
        structured: Optional[StructuredSearchQuery],
        expanded: Optional[ExpandedSearchQuery],
        response: Optional[SearchResponse],
    ) -> SearchSession:
        return self._session_manager.update_session(
            session, query, structured, expanded, response,
        )

    def get_context_chips(self, structured: Optional[StructuredSearchQuery]) -> list[dict]:
        return self._session_manager.get_context_chips(structured)

    def clear_session(self) -> SearchSession:
        return self._session_manager.create_session()
