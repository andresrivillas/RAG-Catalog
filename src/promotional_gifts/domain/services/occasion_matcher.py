from ..entities.commercial_intent import CommercialIntent
from ..entities.product_knowledge import ProductKnowledge


class OccasionMatcher:
    OCCASION_KEYWORDS = {
        "cumpleanos": ["cumple", "fiesta", "celebra", "party", "cumpleaños"],
        "navidad": ["navidad", "navideño", "navideña", "christmas", "navideño"],
        "bienvenida": ["bienvenida", "welcome", "onboarding", "recepcion", "induccion", "inducción"],
        "evento": ["evento", "feria", "congreso", "conferencia", "convencion", "convención"],
        "campana": ["campaña", "campana", "marketing", "promocion", "promoción", "publicidad"],
        "vip": ["vip", "premium", "exclusivo", "lujo", "alta gama", "ejecutivo"],
        "merchandising": ["merchandising", "marca", "logo", "sublimacion", "sublimación", "tampografia", "tampografía"],
    }

    def score(self, intent: CommercialIntent, product: ProductKnowledge) -> float:
        if not intent.occasion:
            return 0.5
        keywords = self.OCCASION_KEYWORDS.get(intent.occasion, [])
        text = " ".join(product.occasion_tags).lower()
        if any(kw in text for kw in keywords):
            return 1.0
        product_text = (
            f"{product.name} {product.description} {product.benefits}".lower()
        )
        if any(kw in product_text for kw in keywords):
            return 0.7
        return 0.2
