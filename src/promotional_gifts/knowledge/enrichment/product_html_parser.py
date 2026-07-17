from dataclasses import dataclass, field
from typing import List, Optional
import re


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
    availability: Optional[int] = None
    breadcrumb: str = ""


# Términos propios de la UI, navegación, inventario, logística, precios y
# marketing del sitio. Nunca deben llegar al Business Engine.
SCRAPER_DENYLIST = {
    # UI / navegación
    "descargar carrusel", "compartir", "productos relacionados",
    "ver más", "ver mas", "leer más", "leer mas", "mostrar más", "mostrar mas",
    "vista rápida", "vista rapida", "quick view", "ampliar imagen", "zoom",
    "galería", "galeria", "carrusel", "slider", "ver todo", "ver todos",
    "siguiente", "anterior", "página", "pagina", "página anterior",
    "página siguiente", "inicio", "home", "menú", "menu", "categorías",
    "categorias", "subcategorías", "subcategorias", "volver", "seguir",
    "continuar", "cerrar", "abrir", "desplegar", "colapsar",
    # Cuenta / sesión / interacción
    "mi cuenta", "iniciar sesión", "iniciar sesion", "registrarse",
    "cerrar sesión", "cerrar sesion", "favoritos", "lista de deseos",
    "comparar", "tabla de comparación", "agregar al carrito",
    "añadir al carrito", "comprar", "carrito", "finalizar compra",
    # Newsletter / promociones / marketing
    "newsletter", "suscríbete", "suscribete", "suscripción", "suscripcion",
    "obtén nuestras últimas ofertas", "obten nuestras ultimas ofertas",
    "próximas llegadas", "proximas llegadas", "nuevos productos",
    "novedades", "más vendidos", "mas vendidos", "ofertas", "promociones",
    "promoción", "promocion", "descuento", "descuentos", "liquidación",
    "liquidacion", "super precio", "superprecio", "precio imperdible",
    "ahorra", "ahorro", "antes", "ahora", "desde", "hasta", "combo",
    # Inventario / logística
    "existencias", "caja máster", "caja master", "caja máster:", "caja master:",
    "precio actualizado", "bodega", "almacén", "almacen", "fecha estimada",
    "orden en tránsito", "orden en transito", "orden en producción",
    "orden en produccion", "total disponible", "disponible", "en stock",
    "sin stock", "agotado", "inventario", "unidades", "unidad", "cantidad",
    "pedido", "envío", "envio", "entrega", "despacho", "transporte",
    "tracking", "guía", "guia", "empaque", "embalaje", "peso", "volumen",
    "dimensiones de envío", "dimensiones de envio", "envío gratis", "envio gratis",
    "tiempo de entrega", "próximamente", "proximamente", "reserva",
    # Precios / moneda
    "precio", "precios", "valor", "costo", "tarifa", "iva", "impuesto",
    "impuestos", "moneda", "cop", "$", "€", "£", "antes:", "ahora:",
    # Códigos / referencias
    "sku", "referencia interna", "código", "codigo", "ean", "upc",
    "marca:", "modelo:", "fabricante",
    # Garantía / legal
    "garantía", "garantia", "términos", "terminos", "condiciones", "política",
    "politica", "privacidad", "copyright", "derechos reservados", "devoluciones",
    "cambios", "reembolso", "preguntas frecuentes", "faq",
    # Contacto / redes
    "síguenos", "siguenos", "redes sociales", "facebook", "instagram", "twitter",
    "linkedin", "whatsapp", "teléfono", "telefono", "contacto", "direccion",
    "dirección", "horario", "atención", "atencion", "sucursal", "oficina principal",
    # Busqueda / filtros
    "buscar", "busqueda", "búsqueda", "filtrar", "ordenar", "resultados",
    "mostrando", "aplicar filtros", "limpiar filtros", "filtrado por",
    # Generic HTML / metadatos
    "nbsp", "script", "style", "html", "body", "href", "src", "class=", "id=",
}


# Materiales comercialmente relevantes para regalos promocionales.
KNOWN_MATERIALS = {
    "acero inoxidable", "acero", "aluminio", "bambú", "bambu", "cartón",
    "carton", "cerámica", "ceramica", "corcho", "cuero", "cuero sintético",
    "cuero sintetico", "madera", "metal", "papel", "plástico", "plastico",
    "poliéster", "poliester", "polipropileno", "policarbonato", "pvc",
    "rpet", "reciclado", "silicona", "vidrio", "algodón", "algodon",
    "neopreno", "nylon", "tela", "yute", "paja", "trigo", "lino", "denim",
    "jeans", "malla", "mesh", "eva", "tpr", "caucho", "goma", "acrílico",
    "acrilico", "sintético", "sintetico", "licra", "lycra", "poliuretano",
    "cromo", "zinc", "titanio", "metalizado", "pet", "polietileno", "abs",
    "melamina", "porcelana", "acero inox", "inox", "piel", "suede", "fieltro",
    "mdf", "bambu natural", "silicon", "termoplastico", "termoplástico",
}


class ProductHtmlParser:
    def parse(self, html: str) -> ScrapedProduct:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        result = ScrapedProduct()

        result.breadcrumb = self._extract_breadcrumb(soup)
        result.availability = self._extract_availability(soup)

        result.description = self._clean_text(
            self._text(soup, ["description", "descripcion", "detalle", "contenido"])
        )
        result.benefits = self._clean_text(
            self._text(soup, ["beneficio", "ventaja", "benefit"])
        )
        result.characteristics = self._clean_text(
            self._text(soup, ["caracteristica", "especificacion", "ficha"])
        )
        result.materials = self._clean_materials(
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

        cat, sub = self._extract_category(soup, result.breadcrumb)
        result.category = cat
        result.subcategory = sub

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

    def _extract_breadcrumb(self, soup) -> str:
        """Extrae el texto del breadcrumb si existe."""
        selectors = [
            ".breadcrumb",
            ".breadcrumbs",
            "nav[aria-label='breadcrumb']",
            "nav[aria-label='Breadcrumb']",
            "[class*='breadcrumb']",
            "[class*='breadcrumbs']",
        ]
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                text = elements[0].get_text(" > ", strip=True)
                text = re.sub(r"\s+", " ", text)
                # Colapsar separadores múltiples y variantes (/, >, \) en uno solo.
                text = re.sub(r"\s*[/\\>]\s*", " > ", text)
                text = re.sub(r"(?:\s*>\s*)+", " > ", text)
                text = re.sub(r"\s+", " ", text).strip(" >")
                if text and text.lower() not in {"inicio", "home"}:
                    # Quitar segmentos iniciales genéricos (Inicio, Home, Productos, Catálogo).
                    parts = [p.strip() for p in text.split(">") if p.strip()]
                    ignore = {"inicio", "home", "productos", "catálogo", "catalogo", "tienda"}
                    while parts and parts[0].lower() in ignore:
                        parts.pop(0)
                    if parts:
                        return " > ".join(parts)
        return ""

    def _extract_availability(self, soup) -> Optional[int]:
        """Extrae las unidades disponibles desde .quantities-product o tablas."""
        # Selector principal del sitio.
        qty = soup.select_one(".quantities-product")
        if qty:
            value = self._parse_stock_number(qty.get_text(" ", strip=True))
            if value is not None:
                return value

        # Tablas con filas "Existencias" / "TOTAL" / "Total disponible".
        for row in soup.find_all(["tr", "li", "div"]):
            text = row.get_text(" ", strip=True).lower()
            if any(label in text for label in ("existencias", "total", "total disponible")):
                value = self._parse_stock_number(text)
                if value is not None:
                    return value

        return None

    def _parse_stock_number(self, text: str) -> Optional[int]:
        """Parsea un número de stock con separador de miles '.' o ','."""
        if not text:
            return None
        # Normalizar: 425.602 -> 425602; 1.234,56 -> 1234.56
        text = text.replace(".", "")
        text = text.replace(",", ".")
        match = re.search(r"\d+(?:\.\d+)?", text)
        if not match:
            return None
        try:
            return int(float(match.group(0)))
        except ValueError:
            return None

    def _extract_category(self, soup, breadcrumb: str) -> tuple:
        """Resuelve categoría y subcategoría preferiblemente desde breadcrumb."""
        cat, sub = self._category_from_breadcrumb(breadcrumb)
        if cat:
            return cat, sub

        cat = self._explicit_category(soup)
        if cat:
            return cat, ""

        # Fallback muy conservador: solo busca etiquetas pequeñas que contengan
        # "categoría" y no el menú completo.
        candidates = []
        for tag in soup.find_all(["span", "div", "p", "td", "li"]):
            text = tag.get_text(" ", strip=True)
            if len(text) > 50:
                continue
            lower = text.lower()
            if "categoría" in lower or "categoria" in lower or "category" in lower:
                cleaned = self._clean_text(text)
                if cleaned:
                    candidates.append(cleaned)
        if candidates:
            return self._clean_text(candidates[0]), ""

        return "", ""

    def _category_from_breadcrumb(self, breadcrumb: str) -> tuple:
        if not breadcrumb:
            return "", ""
        parts = [
            p.strip()
            for p in re.split(r"\s*>\s*|\s*/\s*|\s*\\\s*", breadcrumb)
            if p.strip()
        ]
        # Descartar términos genéricos de navegación.
        ignore = {"inicio", "home", "productos", "catálogo", "catalogo", "tienda"}
        parts = [p for p in parts if p.lower() not in ignore]
        if not parts:
            return "", ""
        # Categoría: último segmento breve; subcategoría: anterior si existe.
        category = parts[-1] if len(parts[-1].split()) <= 4 else ""
        subcategory = parts[-2] if len(parts) >= 2 and len(parts[-2].split()) <= 4 else ""
        return self._clean_text(category), self._clean_text(subcategory)

    def _explicit_category(self, soup) -> str:
        """Busca una etiqueta tipo 'Categoría: X'."""
        for tag in soup.find_all(["span", "div", "p", "td", "li"]):
            text = tag.get_text(" ", strip=True)
            match = re.match(
                r"^(?:categoría|categoria|category)\s*[:\-]\s*(.+)",
                text,
                re.IGNORECASE,
            )
            if match:
                return self._clean_text(match.group(1))
        return ""

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
        """Descarta fragmentos con términos de UI/inventario/logística/precios y
        devuelve un texto limpio y acotado para el Business Engine.
        """
        if not text:
            return ""
        # Eliminar URLs.
        text = re.sub(r"https?://\S+", "", text)
        # Eliminar entidades HTML simples.
        import html

        text = html.unescape(text)

        # Trabajar por líneas/oraciones para poder descartar solo el fragmento
        # contaminado sin perder todo el contenido.
        fragments = [f.strip() for f in text.replace("\r", "\n").split("\n") if f.strip()]
        if not fragments:
            fragments = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
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

    def _clean_materials(self, text: str) -> str:
        """Conserva solo los términos de material conocidos."""
        if not text:
            return ""
        lower = text.lower()
        found = set()
        # Ordenar de más específico a más genérico para evitar duplicados.
        ordered = sorted(KNOWN_MATERIALS, key=len, reverse=True)
        for term in ordered:
            # Expresión regular con word boundary simple para acero inoxidable, etc.
            pattern = re.escape(term)
            if re.search(pattern, lower):
                found.add(term)
                # No borramos el texto para permitir detectar múltiples.
        if not found:
            return ""
        # Normalizar a minúsculas excepto siglas, para mantener consistencia.
        def _present(term: str) -> str:
            if term in {"rpet", "pvc", "eva", "tpr"}:
                return term.upper()
            if term == "acero inoxidable":
                return "acero inoxidable"
            return term

        return ", ".join(_present(t) for t in sorted(found))

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
