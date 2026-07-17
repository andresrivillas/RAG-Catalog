import time
from typing import Optional

from .models import KnowledgeSet


class KnowledgeCache:
    def __init__(self, ttl_seconds: int = 300) -> None:
        self._data: Optional[KnowledgeSet] = None
        self._loaded_at: float = 0
        self._ttl = ttl_seconds

    def get(self) -> Optional[KnowledgeSet]:
        if self._data is not None and (time.monotonic() - self._loaded_at) < self._ttl:
            return self._data
        return None

    def set(self, data: KnowledgeSet) -> None:
        self._data = data
        self._loaded_at = time.monotonic()

    def invalidate(self) -> None:
        self._data = None
        self._loaded_at = 0

    def is_fresh(self) -> bool:
        return self._data is not None and (time.monotonic() - self._loaded_at) < self._ttl
