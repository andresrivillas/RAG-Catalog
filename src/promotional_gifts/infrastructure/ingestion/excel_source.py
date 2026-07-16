from pathlib import Path
from typing import List

import pandas as pd

from ...domain.entities.product_knowledge import ProductKnowledge
from ...domain.ports.ingestion_source_port import IngestionSourcePort
from ...domain.value_objects.money import Money


class ExcelIngestionSource(IngestionSourcePort):
    def __init__(self, catalog_path: Path) -> None:
        self.catalog_path = Path(catalog_path)

    def load(self) -> List[ProductKnowledge]:
        if not self.catalog_path.exists():
            raise FileNotFoundError(
                f"El catálogo no existe en: {self.catalog_path}"
            )

        df = pd.read_excel(self.catalog_path)
        products: List[ProductKnowledge] = []

        for _, row in df.iterrows():
            reference = str(row.get("referencia", "")).strip()
            if not reference or reference.lower() == "nan":
                continue

            name = str(row.get("nombreProducto", "")).strip()
            characteristics = str(row.get("caracteristicas", "")).strip()
            description = str(row.get("descripcion", "")).strip()
            price_raw = row.get("precio", 0)
            try:
                price_value = float(price_raw)
            except (ValueError, TypeError):
                price_value = 0.0
            price_description = str(row.get("descripcion_precio", "")).strip()
            additional_prices = str(row.get("precios_adicionales", "")).strip()

            url_raw = str(row.get("url", "")).strip()
            url = self._build_url(reference, name, url_raw)

            products.append(
                ProductKnowledge(
                    reference=reference,
                    name=name,
                    price=Money(amount=price_value, currency="COP"),
                    characteristics=characteristics,
                    description=description,
                    price_description=price_description,
                    additional_prices=additional_prices,
                    url=url,
                )
            )

        return products

    def _build_url(self, reference: str, name: str, url_raw: str) -> str:
        if url_raw and url_raw.lower() != "nan" and url_raw.startswith("http"):
            return url_raw
        slug = self._slugify(name)
        return f"https://catalogospromocionales.com/producto-cataprom/{reference}/{slug}"

    def _slugify(self, text: str) -> str:
        import re
        import unicodedata

        text = unicodedata.normalize("NFKD", text or "").encode(
            "ascii", "ignore"
        ).decode("ascii")
        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
        return text or "producto"
