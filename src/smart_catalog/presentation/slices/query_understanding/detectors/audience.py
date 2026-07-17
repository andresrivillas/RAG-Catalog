import logging
import re
from typing import Optional

logger = logging.getLogger("smart_catalog.query_understanding")

AUDIENCE_PATTERNS: list[tuple[str, str]] = [
    (r"para\s+medicos", "MEDICOS"), (r"para\s+doctor", "MEDICOS"),
    (r"para\s+enfermer", "MEDICOS"),
    (r"para\s+arquitectos", "ARQUITECTOS"),
    (r"para\s+ingenieros", "INGENIEROS"),
    (r"para\s+abogados", "ABOGADOS"),
    (r"para\s+profesores", "PROFESORES"), (r"para\s+maestros", "PROFESORES"),
    (r"para\s+docentes", "PROFESORES"),
    (r"para\s+ninos", "NINOS"), (r"para\s+ninas", "NINOS"),
    (r"para\s+universidad", "UNIVERSITARIOS"),
    (r"para\s+estudiantes", "ESTUDIANTES"),
    (r"para\s+empresa", "EMPRESA"), (r"para\s+empleados", "EMPRESA"),
    (r"para\s+corporativo", "EMPRESA"), (r"corporativos?", "EMPRESA"),
    (r"para\s+oficina", "OFICINA"),
    (r"eventos?", "EVENTOS"), (r"ferias?", "FERIAS"),
    (r"congresos?", "EVENTOS"), (r"convenciones?", "EVENTOS"),
    (r"lanzamiento", "LANZAMIENTO"), (r"cumpleanos", "CUMPLEANOS"),
    (r"boda", "BODA"),
    (r"regalos?\s+empresariales?", "EMPRESA"),
]


def detect_audience(text: str) -> Optional[str]:
    for pattern, audience in AUDIENCE_PATTERNS:
        if re.search(pattern, text):
            logger.debug("Audiencia detectada: %s", audience)
            return audience
    return None


def matched_terms(text: str) -> list[str]:
    terms = []
    for pattern, _ in AUDIENCE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            for mt in match.group(0).split():
                terms.append(mt)
    return terms
