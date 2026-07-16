import re
import unicodedata
from typing import List

from ...domain.entities.proposal_modification_request import ProposalModificationRequest


def _deaccent(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))

PREMIUM_WORDS = [
    "premium", "elegante", "lujo", "lujoso", "exclusivo", "sofisticado",
    "alta gama", "alta calidad", "mejor", "mejora", "mejoralo", "más top",
]
BUDGET_DOWN_WORDS = [
    "barato", "barata", "económico", "economico", "más barato", "reducir",
    "bajemos", "baja", "menos costoso", "recortar", "ajustar presupuesto",
]
ECO_WORDS = [
    "eco", "ecologico", "ecológico", "sostenible", "verde", "reciclado",
    "reciclable", "rpet", "amigable con el ambiente",
]
REMOVE_MATERIAL_WORDS = [
    "plastico", "plástico", "pvc", "acrilico", "acrílico", "silicona",
    "silicona", "metal", "vidrio", "madera", "cuero", "cuerpo",
]
REQUIRE_MATERIAL_WORDS = [
    "plastico", "plástico", "pvc", "acrilico", "acrílico", "silicona",
    "silicona", "metal", "acero", "vidrio", "madera", "cuero", "cuerpo",
    "tela", "textil", "bambu", "bambú", "ceramica", "cerámica",
]
PACKAGING_WORDS = [
    "empaque", "empacado", "embalaje", "bolsa", "caja", "estuche",
    "packaging", "presentacion", "presentación",
]

REPLACE_PATTERNS = [
    r"cambia(?:r)?\s+(?:las|los|la|el)?\s*(.+?)\s+por\s+(?:unas|unos|una|un|las|los|la|el)?\s*(.+)",
    r"sustituye(?:r)?\s+(?:las|los|la|el)?\s*(.+?)\s+por\s+(?:unas|unos|una|un|las|los|la|el)?\s*(.+)",
    r"reemplaza(?:r)?\s+(?:las|los|la|el)?\s*(.+?)\s+por\s+(?:unas|unos|una|un|las|los|la|el)?\s*(.+)",
    r"pon(?:er|me)?\s+(?:unas|unos|una|un|las|los|la|el)?\s*(.+?)\s+en\s+lugar\s+de\s+(?:las|los|la|el)?\s*(.+)",
]
ADD_PATTERNS = [
    r"agrega(?:r)?\s+(?:unas|unos|una|un|las|los|la|el)?\s*(.+)",
    r"anade(?:r)?\s+(?:unas|unos|una|un|las|los|la|el)?\s*(.+)",
    r"anadir\s+(?:unas|unos|una|un|las|los|la|el)?\s*(.+)",
    r"incorpora(?:r)?\s+(?:unas|unos|una|un|las|los|la|el)?\s*(.+)",
    r"pon(?:er|me)?\s+(?:unas|unos|una|un|las|los|la|el)?\s*(.+)",
    r"quiero\s+(?:unas|unos|una|un|las|los|la|el)?\s*(.+?)(?:\s+tambien|\s+adicional|\s+tambien)?$",
]
REMOVE_PATTERNS = [
    r"quita(?:r|le|lo|la)?\s*(?:las|los|la|el)?\s*(.+)",
    r"elimina(?:r)?\s+(?:las|los|la|el)?\s*(.+)",
    r"saca(?:r)?\s+(?:las|los|la|el)?\s*(.+)",
    r"remueve(?:r)?\s+(?:las|los|la|el)?\s*(.+)",
]
CATEGORY_PATTERNS = [
    r"cambia(?:r)?\s+(?:la)?\s*categoria(?:s)?\s+(?:a|por)?\s*(.+)",
    r"pon(?:er)?\s+productos?\s+de\s+(?:categoria|categoría)?\s*(.+)",
    r"quiero\s+(?:solo\s+)?(.+?)\s+(?:en\s+lugar\s+de|instead)",
]


class RefinementAnalyzer:
    def analyze(self, instruction: str) -> ProposalModificationRequest:
        raw = " ".join(instruction.lower().split())
        text = _deaccent(raw)
        req = ProposalModificationRequest(instruction=instruction)

        for mat in REMOVE_MATERIAL_WORDS:
            if mat in text and any(
                w in text for w in ["quita", "sin", "elimina", "evita", "no quiero"]
            ):
                req.action = ProposalModificationRequest.REMOVE_MATERIAL
                req.material = mat
                req.reason = f"Excluir productos con material '{mat}'."
                return req

        budget = self._extract_new_budget(text)
        if budget is not None:
            req.action = ProposalModificationRequest.CHANGE_BUDGET
            req.budget_per_unit = budget
            req.reason = f"Cambiar presupuesto por unidad a {budget:,.0f} COP."
            return req

        if self._match(replace := self._try_patterns(REPLACE_PATTERNS, text)):
            old, new = replace
            req.action = ProposalModificationRequest.REPLACE_PRODUCT
            req.old_product = self._clean(old)
            req.new_product = self._clean(new)
            req.reason = f"Reemplazar '{req.old_product}' por '{req.new_product}'."
            return req

        if re.search(r"^cambia(?:r)?\s+(?:las|los|la|el)?\s*(.+)$", text) and " por " not in text:
            m = re.search(r"^cambia(?:r)?\s+(?:las|los|la|el)?\s*(.+)$", text)
            req.action = ProposalModificationRequest.REPLACE_PRODUCT
            req.old_product = self._clean(m.group(1))
            req.reason = (
                f"Reemplazar '{req.old_product}' por la mejor alternativa disponible."
            )
            return req

        if self._match(remove := self._try_patterns(REMOVE_PATTERNS, text)):
            req.action = ProposalModificationRequest.REMOVE_PRODUCT
            req.old_product = self._clean(remove[0])
            req.reason = f"Eliminar producto relacionado con '{req.old_product}'."
            return req

        for mat in REQUIRE_MATERIAL_WORDS:
            if any(
                w in text
                for w in ["de", "hecho", "quiero", "usa", "usar", "con"]
            ) and re.search(rf"\b{mat}\b", text) and not self._has_any(
                text, ["sin", "quita", "elimina", "no quiero"]
            ):
                req.action = ProposalModificationRequest.REQUIRE_MATERIAL
                req.material = mat
                req.reason = f"Priorizar productos con material '{mat}'."
                return req

        if self._match(add := self._try_patterns(ADD_PATTERNS, text)):
            req.action = ProposalModificationRequest.ADD_PRODUCT
            req.new_product = self._clean(add[0])
            req.reason = f"Agregar producto relacionado con '{req.new_product}'."
            return req

        if self._has_any(text, PREMIUM_WORDS):
            req.action = ProposalModificationRequest.PREMIUM_UPGRADE
            req.reason = "Mejorar el nivel percibido de la propuesta (premium)."
            return req

        if self._has_any(text, BUDGET_DOWN_WORDS):
            req.action = ProposalModificationRequest.BUDGET_REDUCTION
            req.reason = "Reducir el costo de la propuesta."
            return req

        if self._has_any(text, ECO_WORDS):
            req.action = ProposalModificationRequest.ECO_ONLY
            req.reason = "Restringir la propuesta a productos ecológicos."
            return req

        if self._match(cat := self._try_patterns(CATEGORY_PATTERNS, text)):
            req.action = ProposalModificationRequest.CHANGE_CATEGORY
            req.category = self._clean(cat[0])
            req.reason = f"Enfocar la propuesta en categoría '{req.category}'."
            return req

        if self._has_any(text, PACKAGING_WORDS) and self._has_any(
            text, ["regenera", "cambia", "nuevo", "renueva"]
        ):
            req.action = ProposalModificationRequest.REGENERATE_PACKAGING
            req.reason = "Renovar el empaque/presentación de la propuesta."
            return req

        req.action = ProposalModificationRequest.NO_OP
        req.reason = "No se reconoció una modificación aplicable."
        return req

    def _try_patterns(self, patterns, text):
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return [match.group(1), match.group(2)] if match.lastindex and match.lastindex >= 2 else [match.group(1)]
        return None

    def _match(self, value) -> bool:
        return value is not None

    def _clean(self, value: str) -> str:
        value = _deaccent(value)
        stop = [
            "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del",
            "por", "para", "con", "en", "que", "lo", "me", "quiero", "se",
            "sea", "tambien", "adicional", "nuevo", "nueva", "producto",
            "productos", "regalo", "regalos",
        ]
        result = value.strip()
        for s in stop:
            result = re.sub(rf"\b{s}\b", " ", result)
        result = " ".join(result.split())
        return result

    def _has_any(self, text: str, keywords: List[str]) -> bool:
        return any(kw in text for kw in keywords)

    def _extract_new_budget(self, text: str) -> float:
        pattern = r"(\d[\d\.\s]*)\s*(?:cop)?\s*(?:por\s+unidad|presetupuesto|presupuesto|por\s+unidad)"
        match = re.search(r"presupuesto.*?(\d[\d\.\s]*)", text)
        if not match:
            match = re.search(r"(\d[\d\.\s]*)\s*cop\s*por\s*unidad", text)
        if match:
            raw = match.group(1).replace(".", "").replace(" ", "")
            try:
                return float(raw)
            except ValueError:
                return None
        return None
