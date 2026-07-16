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
        "budget": 0.22,
        "commercial": 0.22,
        "diversity": 0.10,
        "category_diversity": 0.08,
        "coherence": 0.15,
        "utility": 0.08,
        "brand": 0.05,
        "premium": 0.04,
        "eco": 0.04,
        "personalization": 0.05,
        "occasion": 0.16,
        "audience": 0.10,
        "balance": 0.06,
    }


def _premium_weights() -> Dict[str, float]:
    return {
        "budget": 0.18,
        "commercial": 0.28,
        "diversity": 0.08,
        "category_diversity": 0.07,
        "coherence": 0.13,
        "utility": 0.05,
        "brand": 0.08,
        "premium": 0.14,
        "eco": 0.02,
        "personalization": 0.06,
        "occasion": 0.13,
        "audience": 0.08,
        "balance": 0.04,
    }


def _budget_weights() -> Dict[str, float]:
    return {
        "budget": 0.26,
        "commercial": 0.18,
        "diversity": 0.10,
        "category_diversity": 0.08,
        "coherence": 0.14,
        "utility": 0.10,
        "brand": 0.04,
        "premium": 0.02,
        "eco": 0.04,
        "personalization": 0.05,
        "occasion": 0.16,
        "audience": 0.10,
        "balance": 0.06,
    }


def _eco_weights() -> Dict[str, float]:
    return {
        "budget": 0.20,
        "commercial": 0.18,
        "diversity": 0.10,
        "category_diversity": 0.08,
        "coherence": 0.14,
        "utility": 0.07,
        "brand": 0.04,
        "premium": 0.03,
        "eco": 0.20,
        "personalization": 0.08,
        "occasion": 0.14,
        "audience": 0.09,
        "balance": 0.05,
    }


MODE_PROFILES: Dict[GenerationMode, ModeProfile] = {
    GenerationMode.BALANCED: ModeProfile(
        mode=GenerationMode.BALANCED,
        utilization_target_min=0.80,
        utilization_target_max=0.90,
        weight_semantic=25,
        weight_occasion=25,
        weight_commercial=30,
        weight_budget_util=20,
        evaluation_weights=_balanced_weights(),
    ),
    GenerationMode.PREMIUM: ModeProfile(
        mode=GenerationMode.PREMIUM,
        utilization_target_min=0.95,
        utilization_target_max=1.00,
        weight_semantic=20,
        weight_occasion=20,
        weight_commercial=35,
        weight_budget_util=25,
        prefer_premium=True,
        evaluation_weights=_premium_weights(),
    ),
    GenerationMode.BUDGET: ModeProfile(
        mode=GenerationMode.BUDGET,
        utilization_target_min=0.60,
        utilization_target_max=0.80,
        weight_semantic=25,
        weight_occasion=25,
        weight_commercial=25,
        weight_budget_util=25,
        prefer_low_cost=True,
        evaluation_weights=_budget_weights(),
    ),
    GenerationMode.ECO: ModeProfile(
        mode=GenerationMode.ECO,
        utilization_target_min=0.80,
        utilization_target_max=0.90,
        weight_semantic=25,
        weight_occasion=25,
        weight_commercial=25,
        weight_budget_util=25,
        prefer_eco=True,
        evaluation_weights=_eco_weights(),
    ),
}


def get_profile(mode: GenerationMode) -> ModeProfile:
    return MODE_PROFILES.get(mode, MODE_PROFILES[GenerationMode.BALANCED])


def build_evaluation_weights(mode: GenerationMode) -> EvaluationWeights:
    return EvaluationWeights(get_profile(mode).evaluation_weights)
