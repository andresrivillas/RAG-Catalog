import logging
import time
from typing import Optional

from config.settings import settings

from ....domain.models.catalog_product import CatalogProduct
from ....infrastructure.vector_store.chroma_catalog_store import (
    ChromaCatalogStore,
    ChromaProductHit,
)

logger = logging.getLogger("smart_catalog.discovery")

COLLECTIONS: dict[str, dict] = {
    "ecologicos": {
        "title": "Productos Ecológicos",
        "icon": "🌱",
        "query": "rpet bambu corcho reciclado algodon ecologico sostenible biodegradable",
        "description": "Productos fabricados con materiales sostenibles y reciclados",
    },
    "premium": {
        "title": "Productos Premium",
        "icon": "⭐",
        "query": "premium ejecutivo elegante lujo corporativo exclusivo alta gama",
        "description": "Productos de alta calidad para clientes corporativos",
    },
    "economicos": {
        "title": "Productos Económicos",
        "icon": "💰",
        "query": "economico barato accesible promocional bajo costo",
        "description": "Productos de bajo costo ideales para presupuestos ajustados",
    },
    "tecnologia": {
        "title": "Tecnología",
        "icon": "💻",
        "query": "tecnologia electronico cargador usb inalambrico cable digital",
        "description": "Productos tecnológicos y accesorios digitales",
    },
    "oficina": {
        "title": "Oficina",
        "icon": "📋",
        "query": "oficina escritorio organizador papeleria agenda lapicero oficina corporativo",
        "description": "Todo para el entorno corporativo y de oficina",
    },
    "bebidas": {
        "title": "Bebidas",
        "icon": "🥤",
        "query": "botella termo mug vaso botella termica taza botellon",
        "description": "Botellas, termos, mugs y vasos personalizables",
    },
    "bolsos": {
        "title": "Bolsos",
        "icon": "👜",
        "query": "bolso bolsa mochila cartera morral bandolera neceser",
        "description": "Bolsos, mochilas y accesorios",
    },
    "mas_vendidos": {
        "title": "Más Vendidos",
        "icon": "🏆",
        "query": "promocional popular corporativo regalo empresarial oferta",
        "description": "Los productos más populares del catálogo",
    },
}


class DiscoveryService:
    def __init__(self, extra_collections: list[dict] = None) -> None:
        self._store = ChromaCatalogStore(
            persist_directory=settings.chroma_dir,
            collection_name=settings.collection_name,
        )
        self._collections = self._build_collections(extra_collections or [])

    def _build_collections(self, extra_collections: list[dict]) -> dict[str, dict]:
        collections = dict(COLLECTIONS)
        for collection in extra_collections:
            key = collection.get("key")
            if not key:
                continue
            collections[key] = {
                k: v for k, v in collection.items() if k != "key"
            }
        return collections

    def get_collections(self) -> list[dict]:
        return [
            {
                "key": key,
                **info,
            }
            for key, info in self._collections.items()
        ]

    def load_collection(
        self,
        collection_key: str,
        limit: int = 20,
    ) -> tuple[list[CatalogProduct], dict]:
        start = time.perf_counter()

        info = self._collections.get(collection_key)
        if not info:
            return [], {}

        query = info["query"]
        hits = self._store.search(query, top_k=limit)

        products = []
        total_price = 0.0
        materials: dict[str, int] = {}
        categories: dict[str, int] = {}

        for hit in hits:
            product = self._hit_to_product(hit)
            products.append(product)
            total_price += product.price

            if product.material:
                for m in product.material.split(","):
                    m = m.strip().lower()
                    if m:
                        materials[m] = materials.get(m, 0) + 1

            if product.category:
                cat = product.category
                categories[cat] = categories.get(cat, 0) + 1

        elapsed = (time.perf_counter() - start) * 1000

        avg_price = total_price / len(products) if products else 0.0
        top_material = max(materials, key=materials.get) if materials else ""
        top_category = max(categories, key=categories.get) if categories else ""

        summary = {
            "count": len(products),
            "avg_price": round(avg_price, 0),
            "top_material": top_material,
            "top_category": top_category,
            "elapsed_ms": round(elapsed, 0),
        }

        logger.info(
            "Coleccion '%s': %d productos en %.0fms | precio prom=%.0f | material=%s | cat=%s",
            collection_key, len(products), elapsed, avg_price, top_material, top_category,
        )

        return products, summary

    def _hit_to_product(self, hit: ChromaProductHit) -> CatalogProduct:
        return CatalogProduct(
            reference=hit.reference,
            name=hit.name,
            description=hit.description,
            category=hit.category,
            subcategory=hit.subcategory,
            price=hit.price,
            currency=hit.currency,
            material=hit.materials,
            colors=hit.colors,
            eco_friendly="eco" in hit.commercial_tags or "ecologico" in hit.category.lower(),
            personalizable="personalizable" in hit.commercial_tags,
            image_url=hit.thumbnail_url or None,
            detail_url=hit.detail_url or None,
            perceived_value_level=hit.perceived_value_level,
            tags=list(set(
                hit.commercial_tags + hit.occasion_tags + hit.audience_tags
            )),
            score=hit.score,
        )
