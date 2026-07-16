from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from .evaluation.proposal_evaluation_engine import EvaluationWeights


class GenerationMode(str, Enum):
    BALANCED = "balanced"
    PREMIUM = "premium"
    BUDGET = "budget"
    ECO = "eco"

    @classmethod
    def parse(cls, value: str) -> "GenerationMode":
        if not value:
            return cls.BALANCED
        normalized = value.strip().lower()
        for mode in cls:
            if mode.value == normalized:
                return mode
        return cls.BALANCED

    @classmethod
    def all_values(cls) -> List[str]:
        return [m.value for m in cls]


@dataclass
class ModeProfile:
    mode: GenerationMode
    # Objetivo de utilizacion del presupuesto utilizable (fraccion 0..1).
    utilization_target_min: float
    utilization_target_max: float
    # Pesos del ProductSelector (suma de los 4 componentes principales ~100).
    weight_semantic: float
    weight_occasion: float
    weight_commercial: float
    weight_budget_util: float
    # Peso del Industry Match (senal principal del Business Engine).
    weight_industry: float = 0.0
    # Ajustes deterministas por modo.
    prefer_eco: bool = False
    prefer_premium: bool = False
    prefer_low_cost: bool = False
    # Pesos de la ScoreCard (EvaluationWeights).
    evaluation_weights: Dict[str, float] = field(default_factory=dict)

    @property
    def utilization_target_mid(self) -> float:
        return (self.utilization_target_min + self.utilization_target_max) / 2.0


def _balanced_weights() -> Dict[str, float]:
    return {
        "budget": 0.24,
        "commercial": 0.24,
        "diversity": 0.12,
        "category_diversity": 0.10,
        "coherence": 0.18,
        "utility": 0.10,
        "brand": 0.06,
        "premium": 0.05,
        "eco": 0.05,
        "personalization": 0.06,
        "occasion": 0.18,
        "audience": 0.14,
        "balance": 0.06,
        "industry": 0.20,
        "complementarity": 0.10,
    }


def _premium_weights() -> Dict[str, float]:
    return {
        "budget": 0.20,
        "commercial": 0.30,
        "diversity": 0.10,
        "category_diversity": 0.08,
        "coherence": 0.15,
        "utility": 0.07,
        "brand": 0.10,
        "premium": 0.18,
        "eco": 0.02,
        "personalization": 0.07,
        "occasion": 0.15,
        "audience": 0.10,
        "balance": 0.04,
        "industry": 0.22,
        "complementarity": 0.10,
    }


def _budget_weights() -> Dict[str, float]:
    return {
        "budget": 0.28,
        "commercial": 0.20,
        "diversity": 0.12,
        "category_diversity": 0.10,
        "coherence": 0.16,
        "utility": 0.12,
        "brand": 0.05,
        "premium": 0.02,
        "eco": 0.05,
        "personalization": 0.06,
        "occasion": 0.18,
        "audience": 0.12,
        "balance": 0.06,
        "industry": 0.18,
        "complementarity": 0.10,
    }


def _eco_weights() -> Dict[str, float]:
    return {
        "budget": 0.22,
        "commercial": 0.20,
        "diversity": 0.12,
        "category_diversity": 0.10,
        "coherence": 0.16,
        "utility": 0.09,
        "brand": 0.05,
        "premium": 0.04,
        "eco": 0.22,
        "personalization": 0.10,
        "occasion": 0.16,
        "audience": 0.11,
        "balance": 0.05,
        "industry": 0.18,
        "complementarity": 0.10,
    }


MODE_PROFILES: Dict[GenerationMode, ModeProfile] = {
    GenerationMode.BALANCED: ModeProfile(
        mode=GenerationMode.BALANCED,
        utilization_target_min=0.90,
        utilization_target_max=0.98,
        weight_semantic=12,
        weight_occasion=18,
        weight_commercial=38,
        weight_budget_util=22,
        weight_industry=30,
        evaluation_weights=_balanced_weights(),
    ),
    GenerationMode.PREMIUM: ModeProfile(
        mode=GenerationMode.PREMIUM,
        utilization_target_min=0.95,
        utilization_target_max=1.00,
        weight_semantic=10,
        weight_occasion=16,
        weight_commercial=40,
        weight_budget_util=24,
        weight_industry=30,
        prefer_premium=True,
        evaluation_weights=_premium_weights(),
    ),
    GenerationMode.BUDGET: ModeProfile(
        mode=GenerationMode.BUDGET,
        utilization_target_min=0.75,
        utilization_target_max=0.95,
        weight_semantic=14,
        weight_occasion=18,
        weight_commercial=36,
        weight_budget_util=24,
        weight_industry=28,
        prefer_low_cost=True,
        evaluation_weights=_budget_weights(),
    ),
    GenerationMode.ECO: ModeProfile(
        mode=GenerationMode.ECO,
        utilization_target_min=0.88,
        utilization_target_max=0.96,
        weight_semantic=12,
        weight_occasion=18,
        weight_commercial=36,
        weight_budget_util=24,
        weight_industry=30,
        prefer_eco=True,
        evaluation_weights=_eco_weights(),
    ),
}


def get_profile(mode: GenerationMode) -> ModeProfile:
    return MODE_PROFILES.get(mode, MODE_PROFILES[GenerationMode.BALANCED])


def build_evaluation_weights(mode: GenerationMode) -> EvaluationWeights:
    return EvaluationWeights(get_profile(mode).evaluation_weights)
