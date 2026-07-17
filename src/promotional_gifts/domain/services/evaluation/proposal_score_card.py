from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CriterionResult:
    name: str
    score: float
    reason: str
    weight: float = 0.0
    contribution: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "score": round(self.score, 2),
            "weight": round(self.weight, 3),
            "contribution": round(self.contribution, 2),
            "reason": self.reason,
        }


@dataclass
class ProposalScoreCard:
    overall_score: float = 0.0
    budget_score: float = 0.0
    commercial_score: float = 0.0
    coherence_score: float = 0.0
    diversity_score: float = 0.0
    category_diversity_score: float = 0.0
    utility_score: float = 0.0
    brand_visibility_score: float = 0.0
    premium_score: float = 0.0
    eco_score: float = 0.0
    personalization_score: float = 0.0
    occasion_score: float = 0.0
    audience_score: float = 0.0
    balance_score: float = 0.0
    industry_score: float = 0.0
    complementarity_score: float = 0.0
    category_quality_score: float = 0.0
    material_cleanliness_score: float = 0.0
    mode_coherence_score: float = 0.0
    availability_score: float = 0.0
    selection_reason_quality_score: float = 0.0
    consistency_score: float = 0.0
    explainability_score: float = 0.0
    criteria: List[CriterionResult] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "overall_score": round(self.overall_score, 2),
            "budget_score": round(self.budget_score, 2),
            "commercial_score": round(self.commercial_score, 2),
            "coherence_score": round(self.coherence_score, 2),
            "diversity_score": round(self.diversity_score, 2),
            "category_diversity_score": round(self.category_diversity_score, 2),
            "utility_score": round(self.utility_score, 2),
            "brand_visibility_score": round(self.brand_visibility_score, 2),
            "premium_score": round(self.premium_score, 2),
            "eco_score": round(self.eco_score, 2),
            "personalization_score": round(self.personalization_score, 2),
            "occasion_score": round(self.occasion_score, 2),
            "audience_score": round(self.audience_score, 2),
            "balance_score": round(self.balance_score, 2),
            "industry_score": round(self.industry_score, 2),
            "complementarity_score": round(self.complementarity_score, 2),
            "category_quality_score": round(self.category_quality_score, 2),
            "material_cleanliness_score": round(self.material_cleanliness_score, 2),
            "mode_coherence_score": round(self.mode_coherence_score, 2),
            "availability_score": round(self.availability_score, 2),
            "selection_reason_quality_score": round(self.selection_reason_quality_score, 2),
            "consistency_score": round(self.consistency_score, 2),
            "explainability_score": round(self.explainability_score, 2),
            "criteria": [c.to_dict() for c in self.criteria],
            "observations": self.observations,
        }
