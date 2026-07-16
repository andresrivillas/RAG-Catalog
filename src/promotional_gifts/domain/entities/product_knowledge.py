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
    url: str = ""
    benefits: str = ""
    materials: str = ""
    dimensions: str = ""
    capacity: str = ""
    colors: str = ""
    images: List[str] = field(default_factory=list)
    category: str = ""
    subcategory: str = ""
    recommendations: str = ""
    customization: str = ""
    keywords: List[str] = field(default_factory=list)
    occasion_tags: List[str] = field(default_factory=list)
    audience_tags: List[str] = field(default_factory=list)
    commercial_tags: List[str] = field(default_factory=list)
    embedding_text: str = ""
    embedding: list = field(default_factory=list)
    perceived_value_level: str = "medio"
    enriched: bool = False

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
