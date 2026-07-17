from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DetectorGap:
    query: str = ""
    detector: str = ""
    expected: list[str] = field(default_factory=list)
    detected: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class SynonymCandidate:
    term: str = ""
    normalized: str = ""
    frequency: int = 0
    examples: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class CategoryCandidate:
    term: str = ""
    category: str = ""
    frequency: int = 0
    examples: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class MaterialCandidate:
    term: str = ""
    normalized: str = ""
    frequency: int = 0
    examples: list[str] = field(default_factory=list)


@dataclass
class AudienceCandidate:
    pattern: str = ""
    audience: str = ""
    frequency: int = 0
    examples: list[str] = field(default_factory=list)


@dataclass
class Recommendation:
    category: str = ""
    description: str = ""
    impact: str = "bajo"
    frequency: int = 0
    affected_queries: list[str] = field(default_factory=list)
    confidence: float = 0.0
    effort: str = "bajo"


@dataclass
class AnalysisReport:
    detector_gaps: list[DetectorGap] = field(default_factory=list)
    low_detection_queries: list[str] = field(default_factory=list)
    low_precision_queries: list[str] = field(default_factory=list)
    synonym_candidates: list[SynonymCandidate] = field(default_factory=list)
    category_candidates: list[CategoryCandidate] = field(default_factory=list)
    material_candidates: list[MaterialCandidate] = field(default_factory=list)
    audience_candidates: list[AudienceCandidate] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    unused_rules: list[str] = field(default_factory=list)
    total_evaluated: int = 0
    avg_confidence: float = 0.0
