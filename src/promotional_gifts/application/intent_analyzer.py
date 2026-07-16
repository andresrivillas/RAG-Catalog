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
        intent.budget_total = self._extract_budget(
            normalized, total=True
        )
        intent.budget_per_unit = self._extract_budget(
            normalized, total=False
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
            match = re.search(r"(\d[\d\.]*)", text)
        if not match:
            return None
        value = float(match.group(1).replace(".", ""))
        return int(value)

    def _extract_budget(
        self, text: str, total: bool
    ) -> Optional[float]:
        if total:
            pattern = r"(\d[\d\.\s]*)\s*(?:cop)?\s*(?:de\s+)?presupuesto\s+(?:total|maximo|máximo)"
        else:
            pattern = r"(\d[\d\.\s]*)\s*(?:cop)?\s*por\s+unidad"

        match = re.search(pattern, text)
        if not match:
            return None
        raw = match.group(1).replace(".", "").replace(" ", "")
        try:
            return float(raw)
        except ValueError:
            return None
