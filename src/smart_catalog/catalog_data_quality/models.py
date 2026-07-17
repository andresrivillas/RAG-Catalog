from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DetectedProblem:
    code: str = ""
    severity: str = "medium"
    field: str = ""
    description: str = ""
    suggestion: str = ""


@dataclass
class CatalogQuality:
    product_reference: str = ""
    product_name: str = ""
    data_quality_score: float = 0.0
    completeness_score: float = 0.0
    metadata_score: float = 0.0
    commercial_score: float = 0.0
    classification_score: float = 0.0
    searchability_score: float = 0.0
    evidence_score: float = 0.0
    classification_level: str = "critico"
    missing_fields: list[str] = field(default_factory=list)
    suggested_fields: list[str] = field(default_factory=list)
    detected_problems: list[DetectedProblem] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    improvement_priority: float = 0.0
    has_family: bool = False
    has_materials: bool = False
    has_description: bool = False
    has_tags: bool = False
    has_colors: bool = False
    has_commercial_knowledge_strong: bool = False
    category_is_generic: bool = False
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "product_reference": self.product_reference,
            "product_name": self.product_name,
            "data_quality_score": round(self.data_quality_score, 4),
            "completeness_score": round(self.completeness_score, 4),
            "metadata_score": round(self.metadata_score, 4),
            "commercial_score": round(self.commercial_score, 4),
            "classification_score": round(self.classification_score, 4),
            "searchability_score": round(self.searchability_score, 4),
            "evidence_score": round(self.evidence_score, 4),
            "classification_level": self.classification_level,
            "missing_fields": self.missing_fields,
            "suggested_fields": self.suggested_fields,
            "detected_problems": [p.__dict__ for p in self.detected_problems],
            "recommendations": self.recommendations,
            "improvement_priority": round(self.improvement_priority, 4),
            "has_family": self.has_family,
            "has_materials": self.has_materials,
            "has_description": self.has_description,
            "has_tags": self.has_tags,
            "has_colors": self.has_colors,
            "has_commercial_knowledge_strong": self.has_commercial_knowledge_strong,
            "category_is_generic": self.category_is_generic,
        }


CLASSIFICATION_LEVELS = [
    (0.90, "excelente"),
    (0.70, "bueno"),
    (0.50, "aceptable"),
    (0.30, "pobre"),
    (0.00, "critico"),
]


def classify_score(score: float) -> str:
    for threshold, level in CLASSIFICATION_LEVELS:
        if score >= threshold:
            return level
    return "critico"
