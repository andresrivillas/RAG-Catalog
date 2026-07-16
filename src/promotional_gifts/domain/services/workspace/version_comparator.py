from dataclasses import dataclass, field
from typing import List, Optional

from ...entities.proposal_document import ProposalDocument


@dataclass
class VersionComparison:
    root_id: str
    from_version: int
    to_version: int
    added_products: List[str] = field(default_factory=list)
    removed_products: List[str] = field(default_factory=list)
    budget_change: float = 0.0
    per_unit_change: float = 0.0
    score_change: float = 0.0
    description_changed: bool = False
    observations: List[str] = field(default_factory=list)


class VersionComparator:
    def compare(
        self, older: ProposalDocument, newer: ProposalDocument
    ) -> VersionComparison:
        old_items = {it.reference: it.name for it in older.proposal.items}
        new_items = {it.reference: it.name for it in newer.proposal.items}

        added = [name for ref, name in new_items.items() if ref not in old_items]
        removed = [name for ref, name in old_items.items() if ref not in new_items]

        comparison = VersionComparison(
            root_id=older.root_id,
            from_version=older.version,
            to_version=newer.version,
            added_products=added,
            removed_products=removed,
            budget_change=(
                newer.proposal.total_cost.amount - older.proposal.total_cost.amount
            ),
            per_unit_change=(
                newer.proposal.per_unit_cost.amount
                - older.proposal.per_unit_cost.amount
            ),
            score_change=newer.proposal.score - older.proposal.score,
            description_changed=(
                older.proposal.commercial_description
                != newer.proposal.commercial_description
            ),
        )

        if added:
            comparison.observations.append(
                f"Productos agregados ({len(added)}): {', '.join(added)}."
            )
        if removed:
            comparison.observations.append(
                f"Productos eliminados ({len(removed)}): {', '.join(removed)}."
            )
        comparison.observations.append(
            f"Presupuesto: {older.proposal.total_cost.amount:,.0f} -> "
            f"{newer.proposal.total_cost.amount:,.0f} COP "
            f"({comparison.budget_change:+,.0f})."
        )
        comparison.observations.append(
            f"Score: {older.proposal.score:.1f} -> {newer.proposal.score:.1f} "
            f"({comparison.score_change:+.1f})."
        )
        if comparison.description_changed:
            comparison.observations.append("La descripcion comercial cambio.")
        return comparison
