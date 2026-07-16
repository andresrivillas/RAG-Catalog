from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..entities.commercial_intent import CommercialIntent
from ..entities.commercial_proposal import CommercialProposal
from ..services.budget_plan import BudgetPlan


@dataclass
class ProposalSetStatistics:
    total_proposals: int = 0
    total_products_considered: int = 0
    unique_products_used: int = 0
    reused_products: int = 0
    reuse_ratio: float = 0.0
    shared_product_count: int = 0
    shared_product_ratio: float = 0.0
    category_coverage: int = 0
    max_similarity: float = 0.0
    avg_similarity: float = 0.0
    budget_utilization_min: float = 0.0
    budget_utilization_max: float = 0.0
    budget_utilization_avg: float = 0.0
    reused_references: List[str] = field(default_factory=list)
    shared_references: List[str] = field(default_factory=list)
    category_list: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_proposals": self.total_proposals,
            "total_products_considered": self.total_products_considered,
            "unique_products_used": self.unique_products_used,
            "reused_products": self.reused_products,
            "reuse_ratio": round(self.reuse_ratio, 3),
            "shared_product_count": self.shared_product_count,
            "shared_product_ratio": round(self.shared_product_ratio, 3),
            "category_coverage": self.category_coverage,
            "max_similarity": round(self.max_similarity, 3),
            "avg_similarity": round(self.avg_similarity, 3),
            "budget_utilization_min": round(self.budget_utilization_min, 1),
            "budget_utilization_max": round(self.budget_utilization_max, 1),
            "budget_utilization_avg": round(self.budget_utilization_avg, 1),
            "reused_references": list(self.reused_references),
            "shared_references": list(self.shared_references),
            "category_list": list(self.category_list),
            "warnings": list(self.warnings),
        }


@dataclass
class ProposalSet:
    """Conjunto global de propuestas comerciales construidas en una unica
    pasada por el Business Engine con diversidad garantizada.

    El LLM (CommercialWriter) se invoca UNA sola vez con todo el set en
    contexto para redactar las descripciones especificas de cada propuesta.
    """

    intent: CommercialIntent
    budget_plan: BudgetPlan
    proposal_count: int
    proposals: List[CommercialProposal] = field(default_factory=list)
    global_observations: List[str] = field(default_factory=list)
    generation_strategy: str = "global_diversity"
    reused_products: List[str] = field(default_factory=list)
    statistics: Optional[ProposalSetStatistics] = None

    @property
    def all_references(self) -> List[str]:
        refs: List[str] = []
        for p in self.proposals:
            refs.extend(it.reference for it in p.items)
        return refs

    def to_dict(self) -> dict:
        stats = self.statistics.to_dict() if self.statistics else {}
        return {
            "intent": {
                "occasion": self.intent.occasion,
                "quantity": self.intent.quantity,
                "budget_per_unit": self.intent.budget_per_unit,
                "budget_total": self.intent.budget_total,
                "target_audience": self.intent.target_audience,
                "eco": self.intent.eco,
                "personalizable": self.intent.personalizable,
                "industry": self.intent.industry,
            },
            "budget_plan": {
                "total_budget": self.budget_plan.total_budget,
                "spendable_budget": self.budget_plan.spendable_budget,
                "per_unit_ceiling": self.budget_plan.per_unit_ceiling,
                "quantity": self.budget_plan.quantity,
            },
            "proposal_count": self.proposal_count,
            "generation_strategy": self.generation_strategy,
            "global_observations": list(self.global_observations),
            "reused_products": list(self.reused_products),
            "statistics": stats,
            "proposals": [self._proposal_summary(p) for p in self.proposals],
        }

    def _proposal_summary(self, p: CommercialProposal) -> dict:
        return {
            "name": p.name,
            "score": round(p.score, 1),
            "generation_mode": p.generation_mode,
            "total_cost": p.total_cost.amount if p.total_cost else 0.0,
            "per_unit_cost": p.per_unit_cost.amount if p.per_unit_cost else 0.0,
            "warnings": list(p.warnings),
            "occasion": p.occasion,
            "target_audience": p.target_audience,
            "commercial_description": p.commercial_description,
            "items": [
                {
                    "reference": it.reference,
                    "name": it.name,
                    "unit_price": it.unit_price.amount if it.unit_price else 0.0,
                    "quantity": it.quantity,
                    "role": it.role,
                    "category": it.category,
                    "materials": it.materials,
                    "selection_reason": it.selection_reason,
                    "detail_url": it.detail_url,
                }
                for it in p.items
            ],
        }
