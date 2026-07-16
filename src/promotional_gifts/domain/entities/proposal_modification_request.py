from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ProposalModificationRequest:
    instruction: str
    action: str = ""
    old_product: Optional[str] = None
    new_product: Optional[str] = None
    material: Optional[str] = None
    category: Optional[str] = None
    budget_per_unit: Optional[float] = None
    added_references: List[str] = field(default_factory=list)
    removed_references: List[str] = field(default_factory=list)
    reason: str = ""

    ADD_PRODUCT = "add_product"
    REMOVE_PRODUCT = "remove_product"
    REPLACE_PRODUCT = "replace_product"
    CHANGE_BUDGET = "change_budget"
    PREMIUM_UPGRADE = "premium_upgrade"
    BUDGET_REDUCTION = "budget_reduction"
    ECO_ONLY = "eco_only"
    REMOVE_MATERIAL = "remove_material"
    REQUIRE_MATERIAL = "require_material"
    CHANGE_CATEGORY = "change_category"
    REGENERATE_PACKAGING = "regenerate_packaging"
    NO_OP = "no_op"
