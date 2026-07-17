from ....domain.ports.vector_store_port import VectorStorePort
from ..context import ProposalContext


class RetrievalStage:
    def __init__(self, vector_store: VectorStorePort) -> None:
        self._vector_store = vector_store

    def execute(self, ctx: ProposalContext) -> None:
        query = self._expand_query(ctx.text, ctx.intent)
        ctx.candidates = self._vector_store.search(query=query, top_k=ctx.top_k)
        if not ctx.candidates and ctx.text:
            ctx.candidates = self._vector_store.search(query=ctx.text, top_k=ctx.top_k)

    def _expand_query(self, text: str, intent) -> str:
        try:
            from ...services.query_expander import expand_query
        except Exception:
            return text
        parts = [text]
        if intent and intent.occasion:
            parts.append(intent.occasion)
        if intent and intent.target_audience:
            parts.append(intent.target_audience)
        if intent and intent.industry:
            parts.append(intent.industry)
        expanded = expand_query(" ".join(p for p in parts if p))
        return expanded or text
