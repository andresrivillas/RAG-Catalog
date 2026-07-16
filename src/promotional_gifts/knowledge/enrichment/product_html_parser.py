from dataclasses import dataclass, field
from typing import List


@dataclass
class ScrapedProduct:
    description: str = ""
    benefits: str = ""
    characteristics: str = ""
    materials: str = ""
    dimensions: str = ""
    capacity: str = ""
    colors: str = ""
    images: List[str] = field(default_factory=list)
    category: str = ""
    subcategory: str = ""
    recommendations: str = ""
    customization: str = ""


class ProductHtmlParser:
    def parse(self, html: str) -> ScrapedProduct:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        result = ScrapedProduct()

        result.description = self._text(
            soup, ["description", "descripcion", "detalle", "contenido"]
        )
        result.benefits = self._text(soup, ["beneficio", "ventaja", "benefit"])
        result.characteristics = self._text(
            soup, ["caracteristica", "especificacion", "ficha"]
        )
        result.materials = self._text(soup, ["material", "composicion"])
        result.dimensions = self._text(soup, ["dimension", "medida", "talla"])
        result.capacity = self._text(soup, ["capacidad", "volumen", "contenido"])
        result.colors = self._text(soup, ["color", "color"])
        result.category = self._text(soup, ["categoria", "category"])
        result.subcategory = self._text(soup, ["subcategoria", "subcategory"])
        result.recommendations = self._text(
            soup, ["recomendad", "sugerencia", "relacionado"]
        )
        result.customization = self._text(
            soup, ["personaliz", "grabado", "customiz"]
        )
        result.images = self._images(soup)
        return result

    def _text(self, soup, keywords: List[str]) -> str:
        candidates = []
        for tag in soup.find_all(["p", "li", "span", "div", "td", "h2", "h3"]):
            text = tag.get_text(" ", strip=True)
            cls = " ".join(tag.get("class", []))
            if any(k in text.lower() or k in cls.lower() for k in keywords):
                if len(text) > 3:
                    candidates.append(text)
        if not candidates:
            return ""
        return " ".join(candidates)[:1000]

    def _images(self, soup) -> List[str]:
        images = []
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or ""
            if src and src.startswith("http"):
                images.append(src)
        return images[:5]
