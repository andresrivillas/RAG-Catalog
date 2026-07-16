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
    thumbnail_url: str = ""
    image_urls: List[str] = field(default_factory=list)
    category: str = ""
    subcategory: str = ""
    recommendations: str = ""
    customization: str = ""


# Términos propios de la UI, navegación, inventario y logística del sitio.
# Nunca deben llegar al Business Engine.
SCRAPER_DENYLIST = {
    "descargar carrusel", "compartir", "productos relacionados", "existencias",
    "caja máster", "caja master", "precio actualizado", "bodega",
    "fecha estimada", "orden en tránsito", "orden en transito",
    "total disponible", "disponible", "en stock", "sin stock", "inventario",
    "unidades", "unidad", "cantidad", "pedido", "envío", "envio",
    "entrega", "despacho", "transporte", "tracking", "guía", "guia",
    "agregar al carrito", "añadir al carrito", "comprar", "carrito",
    "ver más", "ver mas", "leer más", "leer mas", "mostrar más", "mostrar mas",
    "vista rápida", "vista rapida", "quick view", "sku", "referencia interna",
    "código", "codigo", "ean", "upc", "marca:", "modelo:", "fabricante",
    "garantía", "garantia", "términos", "terminos", "condiciones", "política",
    "politica", "privacidad", "copyright", "derechos reservados", "síguenos",
    "siguenos", "redes sociales", "facebook", "instagram", "twitter", "linkedin",
    "whatsapp", "teléfono", "telefono", "contacto", "direccion", "dirección",
    "horario", "atención", "atencion", "sucursal", "oficina principal",
    "volver", "siguiente", "anterior", "página", "pagina", "buscar", "busqueda",
    "filtrar", "ordenar", "resultados", "mostrando", "página anterior",
    "página siguiente", "inicio", "home", "menú", "menu", "categorías", "categorias",
    "mi cuenta", "iniciar sesión", "registrarse", "cerrar sesión", "cerrar sesion",
    "favoritos", "lista de deseos", "comparar", "tabla de comparación",
}


class ProductHtmlParser:
    def parse(self, html: str) -> ScrapedProduct:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        result = ScrapedProduct()

        result.description = self._clean_text(
            self._text(soup, ["description", "descripcion", "detalle", "contenido"])
        )
        result.benefits = self._clean_text(
            self._text(soup, ["beneficio", "ventaja", "benefit"])
        )
        result.characteristics = self._clean_text(
            self._text(soup, ["caracteristica", "especificacion", "ficha"])
        )
        result.materials = self._clean_text(
            self._text(soup, ["material", "composicion"])
        )
        result.dimensions = self._clean_text(
            self._text(soup, ["dimension", "medida", "talla"])
        )
        result.capacity = self._clean_text(
            self._text(soup, ["capacidad", "volumen", "contenido"])
        )
        result.colors = self._clean_text(
            self._text(soup, ["color", "color"])
        )
        result.category = self._clean_text(
            self._text(soup, ["categoria", "category"])
        )
        result.subcategory = self._clean_text(
            self._text(soup, ["subcategoria", "subcategory"])
        )
        result.recommendations = self._clean_text(
            self._text(soup, ["recomendad", "sugerencia", "relacionado"])
        )
        result.customization = self._clean_text(
            self._text(soup, ["personaliz", "grabado", "customiz"])
        )
        images = self._images(soup)
        result.images = images
        if images:
            result.thumbnail_url = images[0]
            result.image_urls = images
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

    def _clean_text(self, text: str) -> str:
        """Descarta fragmentos con términos de UI/inventario/logística y
        devuelve un texto limpio y acotado para el Business Engine.
        """
        if not text:
            return ""
        # Trabajar por líneas/oraciones para poder descartar solo el fragmento
        # contaminado sin perder todo el contenido.
        fragments = [f.strip() for f in text.replace("\r", "\n").split("\n") if f.strip()]
        if not fragments:
            fragments = [s.strip() for s in text.split(".") if s.strip()]
        cleaned_fragments = []
        for fragment in fragments:
            lower = fragment.lower()
            if any(deny in lower for deny in SCRAPER_DENYLIST):
                continue
            cleaned_fragments.append(fragment)
        cleaned = " ".join(cleaned_fragments)
        cleaned = " ".join(cleaned.split())
        # Acotar para evitar arrastre de bloques masivos.
        return cleaned[:500].strip()

    def _images(self, soup) -> List[str]:
        images = []
        seen = set()

        gallery = soup.select(".gallery-top img, .swiper-slide img")
        if gallery:
            for img in gallery:
                src = img.get("src") or img.get("data-src") or ""
                if self._valid_gallery_image(src, seen):
                    seen.add(src)
                    images.append(src)
            if images:
                return images[:10]

        zoom_imgs = soup.select("a.img_zoom img")
        if zoom_imgs:
            for img in zoom_imgs:
                src = img.get("src") or img.get("data-src") or ""
                if self._valid_gallery_image(src, seen):
                    seen.add(src)
                    images.append(src)
            if images:
                return images[:10]

        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or ""
            if self._valid_gallery_image(src, seen):
                seen.add(src)
                images.append(src)
        return images[:10]

    @staticmethod
    def _valid_gallery_image(src: str, seen: set) -> bool:
        if not src or not src.startswith("http"):
            return False
        low = src.lower()
        if any(
            skip in low
            for skip in [
                "logo", "icon", "pixel", "placeholder", "related",
                "banner", "publicidad", "-ico", "ico.", "/ico",
            ]
        ):
            return False
        if src in seen:
            return False
        return True
