import re
from typing import Dict, List, Optional

from ..domain.entities.commercial_intent import CommercialIntent
from ..domain.ports.intent_analyzer_port import IntentAnalyzerPort

OCCASIONS: Dict[str, List[str]] = {
    "cumpleanos": ["cumpleaños", "cumpleanos", "birthday", "cumple"],
    "navidad": ["navidad", "navidades", "christmas", "navideño", "navideña"],
    "bienvenida": ["bienvenida", "bienvenido", "welcome", "onboarding"],
    "evento": ["evento", "eventos", "feria", "congreso", "conferencia"],
    "campana": ["campaña", "campana", "marketing", "promocion", "promoción"],
}

AUDIENCES: Dict[str, List[str]] = {
    "mujeres": ["mujer", "mujeres", "femenino", "femenina"],
    "hombres": ["hombre", "hombres", "masculino", "masculina"],
    "ninos": ["niño", "niña", "niños", "niñas", "infantil", "kids"],
}

ATTRIBUTE_KEYWORDS = {
    "eco": ["eco", "ecologico", "ecológico", "sostenible", "sustainable", "rpet"],
    "personalizable": [
        "personalizable",
        "personalizar",
        "customizable",
        "logo",
        "grabado",
        "marca",
    ],
}


class IntentAnalyzer(IntentAnalyzerPort):
    def analyze(self, text: str) -> CommercialIntent:
        normalized = self._normalize(text)
        intent = CommercialIntent(raw_text=text)

        intent.occasion = self._match_dict(normalized, OCCASIONS)
        intent.target_audience = self._match_dict(normalized, AUDIENCES)
        intent.eco = self._has_any(normalized, ATTRIBUTE_KEYWORDS["eco"])
        intent.personalizable = self._has_any(
            normalized, ATTRIBUTE_KEYWORDS["personalizable"]
        )
        intent.quantity = self._extract_quantity(normalized)
        intent.budget_total = self._extract_budget_total(normalized)
        # Si ya se detectó un presupuesto total explícito, no se asume ningún
        # presupuesto por unidad para evitar interpretar el total como unitario.
        intent.budget_per_unit = self._extract_budget_per_unit(
            normalized, intent.quantity, intent.budget_total
        )

        if intent.eco:
            intent.generation_mode = "eco"
        return intent

    def _normalize(self, text: str) -> str:
        return " ".join(text.lower().split())

    def _match_dict(self, text: str, mapping: Dict[str, List[str]]) -> Optional[str]:
        for canonical, variants in mapping.items():
            if self._has_any(text, variants):
                return canonical
        return None

    def _has_any(self, text: str, keywords: List[str]) -> bool:
        return any(kw in text for kw in keywords)

    def _extract_quantity(self, text: str) -> Optional[int]:
        pattern = r"(\d[\d\.]*)\s*(?:regalos|unidades|productos|piezas|articulos|artículos)"
        match = re.search(pattern, text)
        if not match:
            return None
        value = float(match.group(1).replace(".", ""))
        return int(value)

    def _parse_number(self, raw: str) -> Optional[float]:
        cleaned = raw.replace(".", "").replace(" ", "")
        try:
            return float(cleaned)
        except ValueError:
            return None

    def _extract_budget_total(self, text: str) -> Optional[float]:
        # Prioridad 2: presupuesto total explícito.
        patterns = [
            r"presupuesto\s+(?:total|global|completo)\s+(?:de\s+)?(\d[\d\.\s]*)",
            r"presupuesto\s+(?:total|global|completo)\s*:\s*(\d[\d\.\s]*)",
            r"total\s+de\s+(?:presupuesto\s+)?(\d[\d\.\s]*)",
            r"presupuesto\s+para\s+las\s+\d[\d\.]*\s+unidades\s+(?:de\s+)?(\d[\d\.\s]*)",
            r"(?:presupuesto|para)\s+(?:de\s+)?(?:las\s+\d[\d\.]*\s+unidades)\s+(\d[\d\.\s]*)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return self._parse_number(match.group(1))
        return None

    def _extract_budget_per_unit(
        self, text: str, quantity: Optional[int], total: Optional[float] = None
    ) -> Optional[float]:
        if total is not None:
            return None
        # Prioridad 1: "por unidad" es la forma inequívoca de presupuesto por unidad.
        per_unit_patterns = [
            r"(\d[\d\.\s]*)\s*(?:cop|pesos?)?\s*por\s+unidad",
            r"por\s+unidad\s+(?:de\s+)?(\d[\d\.\s]*)\s*(?:cop|pesos?)?",
            r"presupuesto\s+por\s+unidad\s+(?:de\s+)?(\d[\d\.\s]*)",
        ]
        for pattern in per_unit_patterns:
            match = re.search(pattern, text)
            if match:
                return self._parse_number(match.group(1))

        # Prioridad 3: presupuesto unitario implícito.
        # "presupuesto de 25000", "presupuesto 25000", "presupuesto máximo de 25000".
        # El asistente asume presupuesto por unidad cuando hay una cantidad de
        # unidades en la solicitud (comportamiento esperado del comercial).
        implicit_patterns = [
            r"presupuesto\s+(?:maximo|máximo)\s+de\s+(\d[\d\.\s]*)",
            r"presupuesto\s+de\s+(\d[\d\.\s]*)",
            r"presupuesto\s+(\d[\d\.\s]*)",
        ]
        for pattern in implicit_patterns:
            match = re.search(pattern, text)
            if match and quantity:
                return self._parse_number(match.group(1))

        # "máximo 25000", "hasta 25000", "25000 COP", "25000 pesos", "25.000".
        # Solo se aplican si ya hay una cantidad de unidades; de lo contrario
        # sería ambiguo respecto al presupuesto total y se deja sin interpretar.
        if quantity:
            generic_patterns = [
                r"(?:maximo|máximo|hasta)\s+(\d[\d\.\s]*)\s*(?:cop|pesos?)?",
                r"(\d[\d\.\s]*)\s*(?:cop|pesos?)",
            ]
            for pattern in generic_patterns:
                match = re.search(pattern, text)
                if match:
                    return self._parse_number(match.group(1))

        # Prioridad 4 (ambigüedad): si no hay cantidad de unidades y solo aparece
        # un número suelto junto a "presupuesto", no se asume nada para evitar
        # interpretar un total como unitario. Se documenta la decisión:
        # sin cantidad de unidades el número es ambiguo y se omite.
        return None
