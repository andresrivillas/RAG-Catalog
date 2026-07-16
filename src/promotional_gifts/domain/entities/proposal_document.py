from dataclasses import dataclass, field
from typing import List, Optional

from ..entities.commercial_intent import CommercialIntent
from ..entities.commercial_proposal import CommercialProposal
from ..services.evaluation.proposal_score_card import ProposalScoreCard


@dataclass
class RefinementRecord:
    version: int
    instruction: str
    action: str
    affected_product: str = ""
    new_product: str = ""
    result: str = ""

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "instruction": self.instruction,
            "action": self.action,
            "affected_product": self.affected_product,
            "new_product": self.new_product,
            "result": self.result,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RefinementRecord":
        return cls(
            version=data.get("version", 0),
            instruction=data.get("instruction", ""),
            action=data.get("action", ""),
            affected_product=data.get("affected_product", ""),
            new_product=data.get("new_product", ""),
            result=data.get("result", ""),
        )


@dataclass
class ProposalDocument:
    proposal_id: str
    version: int
    created_at: str
    updated_at: str
    original_query: str
    intent: CommercialIntent
    proposal: CommercialProposal
    score_card: Optional[ProposalScoreCard] = None
    refinement_history: List[RefinementRecord] = field(default_factory=list)
    client: str = ""

    @property
    def root_id(self) -> str:
        return self.proposal_id.split("__v")[0] if "__v" in self.proposal_id else self.proposal_id
