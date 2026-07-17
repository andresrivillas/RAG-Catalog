"""Commercial Value Score: valor comercial compuesto de un producto.

No reemplaza los scores existentes; complementa ProductSelector con una señal
adicional de calidad comercial: valor percibido, utilidad, personalización,
permanencia de marca, calidad material, alineación con industria y concepto.
"""
from typing import List, Optional

from ..entities.commercial_intent import CommercialIntent
from ..entities.product_knowledge import ProductKnowledge
from ..services.industry_affinity_service import IndustryAffinityService
from ..services.industry_knowledge import IndustryKnowledge


class CommercialValueScorer:
    """Calcula un score 0..1 de valor comercial para un producto."""

    def __init__(
        self,
        industry_affinity_service: Optional[IndustryAffinityService] = None,
    ) -> None:
        self.affinity = industry_affinity_service or IndustryAffinityService(
            IndustryKnowledge()
        )

    def score(
        self,
        product: ProductKnowledge,
        intent: CommercialIntent,
        concept: Optional[str] = None,
    ) -> float:
        signals = self._signals(product)
        score = 0.0

        # 1. Valor percibido (20%)
        level = product.perceived_value_level or "medio"
        perceived = {"bajo": 0.25, "medio": 0.6, "alto": 0.95}.get(level, 0.5)
        score += 0.20 * perceived

        # 2. Utilidad (20%)
        score += 0.20 * self._utility_score(product, signals)

        # 3. Personalización (15%)
        score += 0.15 * self._personalization_score(product, signals)

        # 4. Permanencia de marca (15%)
        score += 0.15 * self._brand_permanence_score(product, signals)

        # 5. Calidad del material (15%)
        score += 0.15 * self._material_quality_score(product, signals)

        # 6. Alineación con industria (15%)
        affinity = self.affinity.affinity(product, intent)
        score += 0.15 * affinity

        # 7. Alineación con concepto del kit (10% bonus)
        if concept:
            score += 0.10 * self._concept_score(product, concept, signals)

        return max(0.0, min(1.0, score))

    def _signals(self, product: ProductKnowledge) -> str:
        return (
            f"{product.name} {product.description} {product.characteristics} "
            f"{product.materials} {product.benefits} {product.customization} "
            f"{' '.join(product.commercial_tags)} {' '.join(product.audience_tags)} "
            f"{' '.join(product.occasion_tags)}"
        ).lower()

    def _utility_score(self, product: ProductKnowledge, signals: str) -> float:
        utility_terms = [
            "util", "diario", "oficina", "escritorio", "organizador", "soporte",
            "cargador", "usb", "power bank", "botella", "termo", "taza", "mug",
            "paraguas", "maletin", "mochila", "bolso", "viaje", "hogar", "cocina",
            "herramienta", "llavero", "metro", "regla", "calculadora", "memoria",
            "lapicero", "boligrafo", "agenda", "libreta", "cuaderno",
        ]
        hits = sum(1 for term in utility_terms if term in signals)
        return min(1.0, 0.3 + hits * 0.15)

    def _personalization_score(self, product: ProductKnowledge, signals: str) -> float:
        if product.customization:
            return 1.0
        if any(
            kw in signals
            for kw in [
                "logo", "grabado", "personaliz", "marca", "tampografia",
                "tampografía", "sublimacion", "sublimación", "bordado", "impresion",
            ]
        ):
            return 0.85
        return 0.3

    def _brand_permanence_score(self, product: ProductKnowledge, signals: str) -> float:
        # Productos que se usan a diario y se ven en público tienen alta permanencia.
        high_permanence = [
            "oficina", "escritorio", "organizador", "cargador", "usb",
            "power bank", "botella", "termo", "taza", "mug", "paraguas",
            "maletin", "mochila", "bolso", "viaje", "lapicero", "boligrafo",
            "llavero", "agenda", "libreta", "cuaderno",
        ]
        low_permanence = [
            "caja", "empaque", "packaging", "bolsa", "desechable", "descartable",
            "repuesto", "adhesivo", "pegatina", "sticker",
        ]
        if any(term in signals for term in high_permanence):
            return 0.85
        if any(term in signals for term in low_permanence):
            return 0.25
        return 0.5

    def _material_quality_score(self, product: ProductKnowledge, signals: str) -> float:
        premium = [
            "cuero", "acero inoxidable", "metal", "aluminio", "madera", "bambu",
            "bambú", "vidrio", "ceramica", "cerámica", "corcho", "neopreno",
            "poliester", "poliéster", "policarbonato", "silicona",
        ]
        basic = [
            "plastico", "plástico", "carton", "cartón", "papel", "pvc",
            "sintetico", "sintético",
        ]
        if any(m in signals for m in premium):
            return 0.85
        if any(m in signals for m in basic):
            return 0.45
        return 0.5

    def _concept_score(
        self, product: ProductKnowledge, concept: str, signals: str
    ) -> float:
        concept = concept.lower()
        # Sinónimos comunes para conceptos temáticos.
        synonyms = {
            "tecnologia": ["tecnologia", "tecnología", "tech", "gadget", "usb", "cargador", "oficina moderna", "digital"],
            "oficina": ["oficina", "escritorio", "organizador", "set de escritorio", "papeleria", "papelería"],
            "movilidad": ["viaje", "maletin", "maletín", "mochila", "bolso", "paraguas", "tag", "pasaporte"],
            "diseño": ["diseño", "diseno", "elegancia", "premium", "maqueta", "planos", "croquis", "libreta", "agenda"],
            "eco premium": ["eco", "ecologico", "ecológico", "sostenible", "rpet", "bambu", "bambú", "madera", "recicl"],
            "escritorio ejecutivo": ["escritorio", "oficina", "ejecutivo", "premium", "organizador", "agenda", "libreta", "boligrafo", "bolígrafo"],
            "bienestar": ["bienestar", "salud", "hidratacion", "hidratación", "termo", "botella", "higiene", "confort", "desinfectante"],
            "higiene": ["higiene", "desinfectante", "antibacterial", "salud", "mascara", "mascarilla", "tapabocas"],
            "exclusividad": ["exclusivo", "premium", "lujo", "alta gama", "cuero", "metal", "madera", "limitada", "edicion", "edición"],
            "utilidad": ["util", "utilidad", "herramienta", "llavero", "metro", "regla", "navaja", "multiherramienta"],
            "sostenibilidad": ["eco", "ecologico", "ecológico", "sostenible", "rpet", "bambu", "bambú", "recicl"],
        }
        terms = synonyms.get(concept, [concept])
        hits = sum(1 for term in terms if term in signals)
        return min(1.0, 0.2 + hits * 0.25)
