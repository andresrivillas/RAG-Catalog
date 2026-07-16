import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from promotional_gifts.knowledge.enrichment.product_html_parser import ProductHtmlParser


DIRTY_HTML = """
<html>
<body>
<h1>Botella de aluminio premium</h1>
<p>Ideal para hidratación diaria.</p>
<p>Descargar carrusel Compartir Productos relacionados</p>
<p>Material: aluminio. Capacidad: 500 ml.</p>
<p>Existencias: 120 unidades. Bodega: principal. Fecha estimada: 2025-12.</p>
<p>Total disponible. Caja máster. Precio actualizado.</p>
</body>
</html>
"""


def test_parser_cleans_ui_inventory_logistics_terms():
    parser = ProductHtmlParser()
    scraped = parser.parse(DIRTY_HTML)

    dirty_terms = [
        "Descargar carrusel",
        "Compartir",
        "Productos relacionados",
        "Existencias",
        "Bodega",
        "Fecha estimada",
        "Total disponible",
        "Caja máster",
        "Precio actualizado",
    ]
    for field in (
        scraped.description,
        scraped.benefits,
        scraped.characteristics,
        scraped.materials,
        scraped.capacity,
        scraped.recommendations,
        scraped.customization,
    ):
        text = field or ""
        for term in dirty_terms:
            assert term.lower() not in text.lower(), f"'{term}' found in {field!r}"

    assert "aluminio" in scraped.materials
    assert "500 ml" in scraped.capacity
    print("[OK] ProductHtmlParser descarta términos de UI/inventario/logística.")


def test_parser_keeps_allowed_fields():
    parser = ProductHtmlParser()
    scraped = parser.parse(DIRTY_HTML)
    assert scraped.materials
    assert scraped.capacity
    print("[OK] ProductHtmlParser conserva materiales y capacidad útiles.")


def main():
    test_parser_cleans_ui_inventory_logistics_terms()
    test_parser_keeps_allowed_fields()
    print("\nTests de limpieza del scraper pasaron.")


if __name__ == "__main__":
    main()
