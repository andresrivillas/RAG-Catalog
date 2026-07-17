from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SearchMetadata:
    processing_time_ms: float = 0.0
    total_candidates: int = 0
    results_returned: int = 0
    embedding_used: bool = False
    keyword_used: bool = False
    filters_applied: Optional[dict] = None
