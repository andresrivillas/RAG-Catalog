from ..entities.product_knowledge import ProductKnowledge


class RoleClassifier:
    PACKAGING_KEYWORDS = [
        "bolsa", "caja", "empaque", "empaque", "estuche", "maleta", "funDa",
        "funda", "wrapper", "pack", "mochila", "sobre", "etiqueta",
    ]
    PROMOTIONAL_KEYWORDS = [
        "logo", "marca", "branding", "tampografia", "tampografía", "sublimacion",
        "sublimación", "grabado", "personaliz", "regalo", "premio",
    ]
    PREMIUM_CATEGORY = {"tecnologia", "hogar"}
    UTILITY_CATEGORY = {"escritura", "oficina", "viaje"}

    def classify(
        self, product: ProductKnowledge, price_median: float
    ) -> str:
        text = f"{product.name} {product.description}".lower()

        if any(k in text for k in self.PACKAGING_KEYWORDS):
            return "PACKAGING"

        if product.price.amount >= price_median * 1.6:
            return "PREMIUM"

        if any(k in text for k in self.PROMOTIONAL_KEYWORDS):
            return "PROMOTIONAL"

        category = self._category(product)
        if category in self.UTILITY_CATEGORY:
            return "UTILITY"
        if category in self.PREMIUM_CATEGORY and product.price.amount >= price_median:
            return "PREMIUM"

        return "CORE"

    def _category(self, product: ProductKnowledge) -> str:
        text = f"{product.name} {product.description}".lower()
        mapping = {
            "escritura": ["lapiz", "boligrafo", "bolígrafo", "resaltador", "pluma", "portaminas"],
            "bolsos": ["bolsa", "mochila", "cartera", "estuche"],
            "hogar": ["taza", "mug", "termo", "vaso", "plat", "copa"],
            "tecnologia": ["usb", "cargador", "auricular", "altavoz", "speaker", "power bank"],
            "oficina": ["libreta", "cuaderno", "carpeta", "agenda", "notas"],
            "viaje": ["paraguas", "maleta", "neceser", "viaje"],
        }
        for category, keywords in mapping.items():
            if any(kw in text for kw in keywords):
                return category
        return "otros"
