import logging
from typing import Optional

from .models import KnowledgeSet

logger = logging.getLogger("smart_catalog.knowledge_validator")


class KnowledgeValidator:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self, knowledge: KnowledgeSet) -> bool:
        self.errors.clear()
        self.warnings.clear()

        self._check_duplicate_keys(knowledge)
        self._check_circular_synonyms(knowledge)
        self._check_orphan_references(knowledge)
        self._check_material_validity(knowledge)

        if self.errors:
            for e in self.errors:
                logger.error("VALIDATION ERROR: %s", e)
        if self.warnings:
            for w in self.warnings:
                logger.warning("VALIDATION WARNING: %s", w)

        return len(self.errors) == 0

    def _check_duplicate_keys(self, knowledge: KnowledgeSet) -> None:
        seen = set()
        for k in knowledge.product_synonyms:
            if k in seen:
                self.warnings.append(f"Sinonimo duplicado: '{k}'")
            seen.add(k)
        for k in knowledge.materials:
            if k in seen:
                self.warnings.append(f"Material duplicado: '{k}'")
            seen.add(k)

    def _check_circular_synonyms(self, knowledge: KnowledgeSet) -> None:
        for k, v in knowledge.product_synonyms.items():
            if knowledge.product_synonyms.get(v, None) == k:
                self.errors.append(f"Sinonimo circular: {k} <-> {v}")

    def _check_orphan_references(self, knowledge: KnowledgeSet) -> None:
        family_keys = set(k.upper() for k in knowledge.product_families)
        for k, v in knowledge.product_synonyms.items():
            if v.upper() not in family_keys and v not in {"BOLIGRAFO", "LAPIZ", "PLUMA",
                    "VASO", "LIBRETA", "LONCHERA", "MALETA", "PORTAFOLIO",
                    "BILLETERA", "TARJETERO", "BOLSO_TERMICO", "GAFAS",
                    "MONEDERO", "NECESER", "TECLADO", "HUB", "CABLE", "LINTERNA"}:
                self.warnings.append(f"Sinonimo '{k}' apunta a familia desconocida '{v}'")

    def _check_material_validity(self, knowledge: KnowledgeSet) -> None:
        valid_materials = {"METAL", "RPET", "BAMBU", "CORCHO", "ALGODON",
            "MADERA", "PLASTICO", "VIDRIO", "CERAMICA", "CUERO",
            "SINTETICO", "POLIESTER", "POLIPROPILENO", "NEOPRENO",
            "SILICONA", "CAUCHO", "TELA", "YUTE", "LONA", "LIENZO"}
        for k, v in knowledge.materials.items():
            if v not in valid_materials:
                self.warnings.append(f"Material '{k}' apunta a canonico invalido '{v}'")
