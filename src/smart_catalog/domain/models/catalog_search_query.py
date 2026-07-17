from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CatalogSearchQuery:
    text: str
    max_results: int = 20
    filters: Optional[dict] = None
    embedding: Optional[list[float]] = None
