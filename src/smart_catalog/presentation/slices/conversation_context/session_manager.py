import uuid
from typing import Optional

from ....domain.models.expanded_search_query import ExpandedSearchQuery
from ....domain.models.search_response import SearchResponse
from ....domain.models.search_session import SearchSession
from ....domain.models.structured_search_query import StructuredSearchQuery

MAX_HISTORY = 10


class SessionManager:

    def create_session(self) -> SearchSession:
        return SearchSession(
            session_id=str(uuid.uuid4())[:8],
        )

    def update_session(
        self,
        session: SearchSession,
        query: str,
        structured: Optional[StructuredSearchQuery],
        expanded: Optional[ExpandedSearchQuery],
        response: Optional[SearchResponse],
    ) -> SearchSession:
        if session.current_query:
            prev = session.previous_queries
            prev.append(session.current_query)
            if len(prev) > MAX_HISTORY - 1:
                prev = prev[-MAX_HISTORY + 1:]
            session.previous_queries = prev

        entry = {
            "query": query,
            "previous": session.current_query,
        }
        hist = session.history
        hist.append(entry)
        if len(hist) > MAX_HISTORY:
            hist = hist[-MAX_HISTORY:]
        session.history = hist

        session.current_query = query
        session.current_structured = structured
        session.current_expanded = expanded
        session.current_results = response

        return session

    def get_context_chips(self, structured: Optional[StructuredSearchQuery]) -> list[dict]:
        if not structured:
            return []

        chips: list[dict] = []

        for pt in structured.detected_product_types:
            chips.append({"label": pt.capitalize(), "type": "product"})

        for mat in structured.detected_materials:
            chips.append({"label": mat.capitalize(), "type": "material"})

        for cat in structured.detected_categories:
            chips.append({"label": cat, "type": "category"})

        if structured.detected_eco_intent:
            chips.append({"label": "Eco", "type": "eco"})

        if structured.detected_quality_intent == "HIGH_QUALITY":
            chips.append({"label": "Premium", "type": "quality"})

        if structured.detected_price_intent == "LOW_PRICE":
            chips.append({"label": "Precio bajo", "type": "price_low"})
        elif structured.detected_price_intent == "HIGH_PRICE":
            chips.append({"label": "Precio alto", "type": "price_high"})

        for color in structured.detected_colors:
            chips.append({"label": color.capitalize(), "type": "color"})

        return chips
