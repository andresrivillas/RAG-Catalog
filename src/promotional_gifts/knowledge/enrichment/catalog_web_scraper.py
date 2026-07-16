import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class CatalogWebScraper:
    def __init__(
        self,
        timeout: int = 10,
        retries: int = 2,
        user_agent: str = "PromotionalGiftsAI/1.0 (+local)",
    ) -> None:
        self.timeout = timeout
        self.retries = retries
        self.user_agent = user_agent

    def fetch(self, url: str) -> Optional[str]:
        last_error: Optional[str] = None
        for attempt in range(self.retries + 1):
            try:
                response = requests.get(
                    url,
                    timeout=self.timeout,
                    headers={"User-Agent": self.user_agent},
                )
                response.raise_for_status()
                return response.text
            except requests.RequestException as exc:
                last_error = str(exc)
                logger.warning(
                    "Reintento %s/%s fallido para %s: %s",
                    attempt + 1,
                    self.retries + 1,
                    url,
                    exc,
                )
        logger.error("No se pudo descargar %s: %s", url, last_error)
        return None
