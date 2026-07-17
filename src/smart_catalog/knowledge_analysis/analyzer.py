import json
import logging
from collections import Counter
from pathlib import Path
from typing import Optional

from ..search_evaluation.models import TestCase, EvaluationSummary
from .models import (
    DetectorGap, SynonymCandidate, CategoryCandidate,
    MaterialCandidate, AudienceCandidate, Recommendation, AnalysisReport,
)

logger = logging.getLogger("smart_catalog.knowledge_analysis")

KNOWN_FAMILIES = {"USB","BOTELLA","TERMO","LAPICERO","BOLIGRAFO","LAPIZ","PLUMA",
    "MUG","VASO","BOLSO","AGENDA","LIBRETA","CARGADOR","REGALO","LLAVERO","GORRA",
    "CALCULADORA","PARAGUAS","NEVERA","LONCHERA","TOALLA","RELOJ","GAFAS","PULSERA",
    "MONEDERO","NECESER","MOUSE","TECLADO","AUDIFONOS","HUB","CABLE","LINTERNA",
    "ROPA","ORGANIZADOR","MALETA","BOLSO_TERMICO","PORTAFOLIO","BILLETERA","TARJETERO"}

KNOWN_AUDIENCES = {"MEDICOS","ARQUITECTOS","INGENIEROS","ABOGADOS","PROFESORES",
    "NINOS","UNIVERSITARIOS","ESTUDIANTES","EMPRESA","OFICINA","EVENTOS","FERIAS",
    "LANZAMIENTO","CUMPLEANOS","BODA","VIP","BANCOS","CONSTRUCTORAS","BIENVENIDA",
    "MARKETING","VENTAS","RRHH","CAPACITACION","RECEPCION","CONTADORES"}


class KnowledgeGapAnalyzer:

    def analyze(
        self,
        test_cases: list[TestCase],
        evaluation_summary: EvaluationSummary,
        search_results: Optional[list] = None,
        catalog_path: Optional[Path] = None,
    ) -> AnalysisReport:
        report = AnalysisReport(total_evaluated=len(test_cases))

        # 1. Find detector gaps
        for case in test_cases:
            self._find_gaps(case, report)

        # 2. Find low detection queries
        low_detection = []
        for case in test_cases:
            expected = 0
            if case.expected_families: expected += 1
            if case.expected_categories: expected += 1
            if case.expected_materials: expected += 1
            if case.expected_attributes: expected += 1
            if case.expected_audience: expected += 1
            if case.expected_technologies: expected += 1
            if case.expected_capacity: expected += 1
            if expected <= 1:
                low_detection.append(case.query)
        report.low_detection_queries = low_detection

        # 3. Analyze catalog for candidate terms
        if catalog_path and catalog_path.exists():
            self._analyze_catalog(catalog_path, report)

        # 4. Build recommendations from gaps
        self._build_recommendations(report)

        return report

    def _find_gaps(self, case: TestCase, report: AnalysisReport) -> None:
        if case.expected_families:
            for exp in case.expected_families:
                if exp not in KNOWN_FAMILIES:
                    report.detector_gaps.append(DetectorGap(
                        query=case.query, detector="familia",
                        expected=[exp], detected=[],
                    ))
        if case.expected_audience:
            if case.expected_audience not in KNOWN_AUDIENCES:
                report.detector_gaps.append(DetectorGap(
                    query=case.query, detector="audiencia",
                    expected=[case.expected_audience], detected=[],
                ))

    def _analyze_catalog(self, catalog_path: Path, report: AnalysisReport) -> None:
        with open(catalog_path, "r", encoding="utf-8") as f:
            products = json.load(f)

        all_name_tokens = Counter()
        missing_synonyms = []
        missing_categories = []

        for p in products:
            name = (p.get("name") or "").lower().strip()
            cat = (p.get("category") or "").strip()
            mats = (p.get("materials") or "").strip()
            kw = p.get("keywords") or []

            # Tokenize names
            for t in name.split():
                clean = t.strip(" ,.-()/:")
                if clean and len(clean) > 2 and not clean.isdigit():
                    all_name_tokens[clean] += 1

        # Find frequent name tokens that could be synonyms
        for token, freq in all_name_tokens.most_common(200):
            if freq < 5:
                break
            if token in {"produccion","nacional","nuevo","nueva","nuevos","nuevas",
                          "oferta","pack","kit","set","tipo","clase","modelo","color",
                          "medida","medidas","gran","pequeno","grande"}:
                continue

            # Check if this token could be a product type synonym
            for family, variants in self._family_variants().items():
                if token in variants:
                    break
            else:
                # Check if token matches any known material
                from ..presentation.slices.query_understanding.detectors.material import MATERIAL_KEYWORDS
                if token not in MATERIAL_KEYWORDS:
                    # Could be a missing synonym
                    examples = [p.get("name","") for p in products
                                if token in (p.get("name") or "").lower()][:3]
                    report.synonym_candidates.append(SynonymCandidate(
                        term=token, normalized="",
                        frequency=freq, examples=examples[:3],
                    ))

    def _family_variants(self) -> dict:
        from ..presentation.slices.query_understanding.normalizer import SYNONYM_MAP
        variants: dict[str, set] = {}
        for k, v in SYNONYM_MAP.items():
            if v not in variants:
                variants[v] = set()
            variants[v].add(k)
        return variants

    def _build_recommendations(self, report: AnalysisReport) -> None:
        recs: list[Recommendation] = []

        if report.synonym_candidates:
            top = report.synonym_candidates[:5]
            terms = ", ".join(f"'{t.term}' (freq={t.frequency})" for t in top)
            recs.append(Recommendation(
                category="sinonimos",
                description=f"Agregar sinonimos: {terms}",
                impact="alto" if top[0].frequency > 20 else "medio",
                frequency=sum(t.frequency for t in top) // len(top),
                confidence=0.85,
                effort="bajo",
            ))

        for gap in report.detector_gaps:
            recs.append(Recommendation(
                category=f"detector_{gap.detector}",
                description=f"'{' '.join(gap.expected)}' no detectado en: {gap.query}",
                impact="medio",
                frequency=1,
                affected_queries=[gap.query],
                confidence=0.7,
                effort="bajo",
            ))

        if report.low_detection_queries:
            recs.append(Recommendation(
                category="baja_deteccion",
                description=f"{len(report.low_detection_queries)} consultas con baja deteccion",
                impact="alto",
                frequency=len(report.low_detection_queries),
                confidence=0.9,
                effort="medio",
            ))

        recs.sort(key=lambda r: (-r.frequency, "alta" if r.impact == "alto" else "media"))
        report.recommendations = recs
