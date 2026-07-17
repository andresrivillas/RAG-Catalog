from dataclasses import dataclass
from typing import Optional

from .catalog_product import CatalogProduct
from .search_explanation import SearchExplanation


@dataclass
class CatalogSearchResult:
    product: CatalogProduct
    relevance_score: float = 0.0
    rank: int = 0
    explanation: Optional[SearchExplanation] = None
