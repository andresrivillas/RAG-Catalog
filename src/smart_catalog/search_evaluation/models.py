from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExpectedResult:
    reference: str = ""
    name: str = ""
    reason: str = ""


@dataclass
class TestCase:
    query: str = ""
    expected_families: list[str] = field(default_factory=list)
    expected_categories: list[str] = field(default_factory=list)
    expected_materials: list[str] = field(default_factory=list)
    expected_attributes: list[str] = field(default_factory=list)
    expected_audience: Optional[str] = None
    expected_technologies: list[str] = field(default_factory=list)
    expected_capacity: Optional[dict] = None
    expected_results: list[str] = field(default_factory=list)
    expected_count: int = 0
    tags: list[str] = field(default_factory=list)


@dataclass
class DetectorResult:
    families: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    materials: list[str] = field(default_factory=list)
    attributes: list[str] = field(default_factory=list)
    audience: Optional[str] = None
    technologies: list[str] = field(default_factory=list)
    capacity: Optional[dict] = None


@dataclass
class SingleResult:
    query: str = ""
    detector: DetectorResult = field(default_factory=DetectorResult)
    retrieved: list[dict] = field(default_factory=list)
    scores: list[float] = field(default_factory=list)
    explanations: list[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    pipeline_time_ms: float = 0.0


@dataclass
class EvaluationSummary:
    total_cases: int = 0
    precision_at_1: float = 0.0
    precision_at_3: float = 0.0
    precision_at_5: float = 0.0
    recall_at_5: float = 0.0
    mrr: float = 0.0
    ndcg: float = 0.0
    avg_search_time_ms: float = 0.0
    avg_pipeline_time_ms: float = 0.0
    detector_coverage: dict = field(default_factory=dict)
    detector_accuracy: dict = field(default_factory=dict)
    boosted_count: int = 0
    worsened_count: int = 0
    improved_count: int = 0
    ambiguous_queries: list[str] = field(default_factory=list)
    hardest_queries: list[tuple] = field(default_factory=list)
    avg_score: float = 0.0
    score_distribution: dict = field(default_factory=dict)
