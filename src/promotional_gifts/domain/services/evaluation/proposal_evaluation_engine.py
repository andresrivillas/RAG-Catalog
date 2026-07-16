import logging
from typing import Dict, List, Optional

from ...entities.commercial_intent import CommercialIntent
from ...entities.commercial_proposal import CommercialProposal
from ...services.budget_plan import BudgetPlan
from .criteria import ALL_CRITERIA, BaseCriterion
from .proposal_score_card import CriterionResult, ProposalScoreCard

logger = logging.getLogger(__name__)


class EvaluationWeights:
    DEFAULTS: Dict[str, float] = {
        "budget": 0.20,
        "commercial": 0.25,
        "diversity": 0.10,
        "category_diversity": 0.08,
        "coherence": 0.15,
        "utility": 0.07,
        "brand": 0.05,
        "premium": 0.05,
        "eco": 0.05,
        "personalization": 0.05,
        "occasion": 0.15,
        "audience": 0.10,
        "balance": 0.05,
    }

    def __init__(self, mapping: Optional[Dict[str, float]] = None) -> None:
        self._weights = dict(self.DEFAULTS)
        if mapping:
            for key, value in mapping.items():
                self._weights[key] = float(value)

    def get(self, key: str) -> float:
        return self._weights.get(key, 0.0)

    def as_dict(self) -> Dict[str, float]:
        return dict(self._weights)


class ProposalEvaluationEngine:
    def __init__(
        self,
        criteria: Optional[List[BaseCriterion]] = None,
        weights: Optional[EvaluationWeights] = None,
        debug: bool = False,
    ) -> None:
        self.criteria = criteria or [c() for c in ALL_CRITERIA]
        self.weights = weights or EvaluationWeights()
        self.debug = debug

    def evaluate(
        self,
        proposal: CommercialProposal,
        intent: Optional[CommercialIntent] = None,
        plan: Optional[BudgetPlan] = None,
    ) -> ProposalScoreCard:
        card = ProposalScoreCard()

        for criterion in self.criteria:
            result = criterion.evaluate(proposal, intent, plan)
            weight = self.weights.get(criterion.weight_key)
            result.weight = weight
            result.contribution = result.score * weight
            card.criteria.append(result)
            self._store(card, criterion.weight_key, result)

        card.overall_score = sum(c.contribution for c in card.criteria)

        self._observations(card, proposal, intent)

        if self.debug:
            self._log_debug(card, proposal)

        return card

    def _store(
        self, card: ProposalScoreCard, key: str, result: CriterionResult
    ) -> None:
        mapping = {
            "budget": "budget_score",
            "commercial": "commercial_score",
            "coherence": "coherence_score",
            "diversity": "diversity_score",
            "category_diversity": "category_diversity_score",
            "utility": "utility_score",
            "brand": "brand_visibility_score",
            "premium": "premium_score",
            "eco": "eco_score",
            "personalization": "personalization_score",
            "occasion": "occasion_score",
            "audience": "audience_score",
            "balance": "balance_score",
        }
        attr = mapping.get(key)
        if attr:
            setattr(card, attr, result.score)

    def _observations(
        self,
        card: ProposalScoreCard,
        proposal: CommercialProposal,
        intent: Optional[CommercialIntent],
    ) -> None:
        obs: List[str] = []
        top = sorted(card.criteria, key=lambda c: c.score, reverse=True)[:2]
        low = sorted(card.criteria, key=lambda c: c.score)[:2]
        if top:
            obs.append(
                f"Fortaleza: {top[0].name} ({top[0].score:.0f}/100)."
            )
        if low:
            obs.append(
                f"Debilidad: {low[0].name} ({low[0].score:.0f}/100) debe mejorar."
            )
        if card.budget_score < 60:
            obs.append("La propuesta no aprovecha bien el presupuesto.")
        if card.diversity_score < 60:
            obs.append("El kit tiene poca variedad de productos.")
        if card.eco_score == 0 and intent and intent.eco:
            obs.append("Se solicito eco pero ningun producto es sostenible.")
        card.observations = obs

    def _log_debug(self, card: ProposalScoreCard, proposal: CommercialProposal) -> None:
        logger.info("=== ProposalScoreCard [%s] ===", proposal.name or "sin nombre")
        logger.info("overall_score=%.2f", card.overall_score)
        for c in card.criteria:
            logger.info(
                "  %-22s score=%.1f weight=%.2f contrib=%.2f | %s",
                c.name, c.score, c.weight, c.contribution, c.reason,
            )
        for o in card.observations:
            logger.info("  obs: %s", o)
