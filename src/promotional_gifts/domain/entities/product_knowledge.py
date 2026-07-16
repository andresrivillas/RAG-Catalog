from dataclasses import dataclass, field
from typing import List, Optional

from ..value_objects.money import Money


@dataclass
class ProductKnowledge:
    reference: str
    name: str
    price: Money
    characteristics: str = ""
    description: str = ""
    price_description: str = ""
    additional_prices: str = ""
    embedding_text: str = ""
    embedding: list = field(default_factory=list)
    perceived_value_level: str = "medio"

    def to_embedding_text(self) -> str:
        parts = [
            f"Nombre: {self.name}",
            f"Referencia: {self.reference}",
            f"Categoría sugerida: {self.price_description}"
            if self.price_description
            else "",
            f"Características: {self.characteristics}",
            f"Descripción: {self.description}",
        ]
        return "\n".join(p for p in parts if p)
