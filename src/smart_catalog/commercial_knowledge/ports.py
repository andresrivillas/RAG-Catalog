from typing import Optional, Protocol

from ..catalog_knowledge_enrichment.models import CatalogKnowledge


class CatalogKnowledgeRepository(Protocol):
    def get(self, reference: str) -> Optional[CatalogKnowledge]:
        ...

