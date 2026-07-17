"""Commercial Harmony: evalúa cuánto contribuye un producto al concepto de un kit.

Un producto "rompe-kit" baja la armonía comercial y debe ser penalizado aunque
tenga buen score individual.
"""
from typing import List, Optional

from ..entities.commercial_intent import CommercialIntent
from ..entities.product_knowledge import ProductKnowledge


class CommercialHarmonyScorer:
    """Score 0..1 de armonía de un producto dentro de un concepto de kit."""

    # Productos genéricos que suelen romper el concepto de un regalo corporativo.
    KIT_BREAKERS = {
        "metro", "llavero", "llaveros", "regla", "cinta metrica", "cinta métrica",
        "casco", "pito", "silbato", "destapador", "navaja", "martillo",
        "multiherramienta", "herramienta", "repuesto", "adhesivo", "pegatina",
        "sticker", "quitamotas", "quita motas", "aspiradora", "cuerpo en madera",
        "portacomidas", "balaca", "tangram", "juego triqui", "juego desestresante",
        "mini botilito", "botilito sport", "botilito supra", "botilito ergo",
        "coca tradicional", "gancho portacartera", "agarradera",
    }

    # Rompe-kit extremo: debe quedar fuera de propuestas corporativas.
    HARD_BREAKERS = {
        "aspiradora", "coca tradicional", "cuerpo en madera para abanico",
        "gancho portacartera", "agarradera", "repuesto quita motas",
        "pegatina", "sticker", "adhesivo", "juego desestresante", "tangram", "triqui",
        "medidor de masa", "medidor de presion", "medidor de presión", "balaca",
        "llavero metro", "llavero car", "llavero tools", "llavero ml", "llavero pito",
    }

    def harmony(
        self,
        product: ProductKnowledge,
        concept: Optional[str],
        intent: CommercialIntent,
        existing_products: Optional[List[ProductKnowledge]] = None,
    ) -> float:
        signals = self._signals(product)
        score = 1.0

        # Penalización por producto rompe-kit.
        breaker_hits = sum(1 for term in self.KIT_BREAKERS if term in signals)
        if breaker_hits:
            score -= 0.25 * breaker_hits

        # Rompe-kit extremo: penalización drástica.
        if any(term in signals for term in self.HARD_BREAKERS):
            score -= 0.80

        # Penalización por categoría "Otros" sin evidencia clara.
        if (product.category or "").lower() == "otros":
            score -= 0.20

        # Penalización por material básico sin valor agregado.
        if any(m in signals for m in ["plastico", "plástico", "carton", "cartón", "papel"]):
            if not any(m in signals for m in ["personaliz", "logo", "grabado", "marca"]):
                score -= 0.08

        # Alineación con el concepto del kit.
        if concept:
            score += 0.25 * self._concept_alignment(product, concept, signals)

        # Alineación con la industria.
        if intent.industry:
            score += 0.10 * self._industry_alignment(product, intent, signals)

        # Cohesión con productos ya seleccionados.
        if existing_products:
            score += 0.10 * self._cohesion(product, existing_products, signals)

        return max(0.0, min(1.0, score))

    def _signals(self, product: ProductKnowledge) -> str:
        text = (
            f"{product.name} {product.description} {product.characteristics} "
            f"{product.materials} {product.benefits} {product.customization} "
            f"{' '.join(product.commercial_tags)}"
        )
        return text.lower()

    def _concept_alignment(
        self, product: ProductKnowledge, concept: str, signals: str
    ) -> float:
        concept = concept.lower()
        synonyms = {
            "tecnologia": ["tecnologia", "tecnología", "tech", "gadget", "usb", "cargador", "soporte", "celular", "móvil", "oficina moderna"],
            "oficina moderna": ["oficina", "escritorio", "organizador", "set de escritorio", "soporte", "calculadora", "agenda", "libreta"],
            "movilidad": ["viaje", "maletin", "maletín", "mochila", "bolso", "paraguas", "tag", "pasaporte", "neceser"],
            "diseño": ["diseño", "diseno", "elegancia", "premium", "maqueta", "planos", "croquis", "libreta", "agenda", "cuero", "madera"],
            "eco premium": ["eco", "ecologico", "ecológico", "sostenible", "rpet", "bambu", "bambú", "madera", "recicl"],
            "escritorio ejecutivo": ["escritorio", "oficina", "ejecutivo", "premium", "organizador", "agenda", "libreta", "boligrafo", "bolígrafo", "calculadora"],
            "bienestar": ["bienestar", "salud", "hidratacion", "hidratación", "termo", "botella", "higiene", "confort", "desinfectante"],
            "higiene": ["higiene", "desinfectante", "antibacterial", "salud", "mascara", "mascarilla", "tapabocas"],
            "exclusividad": ["exclusivo", "premium", "lujo", "alta gama", "cuero", "metal", "madera", "limitada", "edicion", "edición"],
            "utilidad": ["util", "utilidad", "herramienta", "llavero", "metro", "regla", "navaja", "multiherramienta"],
            "sostenibilidad": ["eco", "ecologico", "ecológico", "sostenible", "rpet", "bambu", "bambú", "recicl"],
        }
        terms = synonyms.get(concept, [concept])
        hits = sum(1 for term in terms if term in signals)
        return min(1.0, 0.2 + hits * 0.25)

    def _industry_alignment(
        self, product: ProductKnowledge, intent: CommercialIntent, signals: str
    ) -> float:
        industry = (intent.industry or "").lower()
        if not industry:
            return 0.5
        preferred = {
            "tecnologia": ["tecnologia", "tecnología", "usb", "cargador", "gadget", "oficina", "escritorio", "organizador"],
            "software": ["tecnologia", "tecnología", "usb", "cargador", "gadget", "oficina", "escritorio", "organizador"],
            "arquitectura": ["diseño", "diseno", "madera", "bambu", "bambú", "metal", "cuero", "premium", "libreta", "agenda", "planos"],
            "clinica": ["salud", "bienestar", "termo", "botella", "higiene", "desinfectante", "oficina", "agenda"],
            "hospital": ["salud", "bienestar", "termo", "botella", "higiene", "desinfectante", "oficina", "agenda"],
            "vip": ["premium", "lujo", "exclusivo", "cuero", "metal", "madera", "alta gama"],
        }
        terms = preferred.get(industry, [])
        if not terms:
            return 0.5
        hits = sum(1 for term in terms if term in signals)
        return min(1.0, 0.2 + hits * 0.25)

    def _cohesion(
        self,
        product: ProductKnowledge,
        existing: List[ProductKnowledge],
        signals: str,
    ) -> float:
        if not existing:
            return 1.0
        scores = []
        for other in existing:
            other_signals = (
                f"{other.name} {other.description} {other.materials} "
                f"{other.category} {other.subcategory}"
            ).lower()
            shared = any(term in other_signals for term in self._tokens(signals))
            scores.append(1.0 if shared else 0.3)
        return sum(scores) / len(scores)

    def _tokens(self, text: str) -> List[str]:
        import re
        return [t for t in re.findall(r"[a-záéíóúñ0-9]+", text) if len(t) > 3]
