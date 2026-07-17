from dataclasses import dataclass, field
from typing import List, Optional

from ...domain.entities.commercial_intent import CommercialIntent
from ...domain.entities.commercial_proposal import CommercialProposal
from ...domain.entities.proposal_set import ProposalSet
from ...domain.services.budget_plan import BudgetPlan
from ...domain.services.generation_mode import GenerationMode
from ...domain.services.product_selector import ScoredProduct


@dataclass
class ProposalContext:
    text: str = ""
    intent: Optional[CommercialIntent] = None
    plan: Optional[BudgetPlan] = None
    mode: GenerationMode = GenerationMode.BALANCED
    top_k: int = 50
    commercial_writer: Optional["CommercialWriter"] = None
    llm_model: str = "llama3.2"
    llm_temperature: float = 0.3
    workspace: Optional["ProposalWorkspace"] = None

    candidates: List = field(default_factory=list)
    scored_products: List[ScoredProduct] = field(default_factory=list)
    proposal_set: Optional[ProposalSet] = None
