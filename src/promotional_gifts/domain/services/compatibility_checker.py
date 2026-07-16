from ..entities.product_knowledge import ProductKnowledge


class CompatibilityChecker:
    INCOMPATIBLE_SAME_CATEGORY = {
        "escritura",
        "hogar",
        "bolsos",
        "oficina",
        "tecnologia",
        "viaje",
    }

    def can_coexist(
        self, a: ProductKnowledge, b: ProductKnowledge
    ) -> bool:
        cat_a = self._category(a)
        cat_b = self._category(b)

        if cat_a == cat_b and cat_a in self.INCOMPATIBLE_SAME_CATEGORY:
            return False

        if self._same_family(a, b):
            return False

        return True

    def _same_family(self, a: ProductKnowledge, b: ProductKnowledge) -> bool:
        base_a = self._base_name(a.name)
        base_b = self._base_name(b.name)
        return base_a != "" and base_a == base_b

    def _base_name(self, name: str) -> str:
        tokens = name.lower().split()
        stop = {"de", "la", "el", "con", "para", "en", "y", "eco", "reciclable"}
        meaningful = [t for t in tokens if t not in stop]
        return meaningful[0] if meaningful else ""

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
