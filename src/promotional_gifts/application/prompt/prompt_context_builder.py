from ...domain.entities.commercial_proposal import CommercialProposal
from ..refinement.proposal_refinement_engine import RefinementLogEntry


class PromptContextBuilder:
    def build(self, proposal: CommercialProposal) -> str:
        lines = []
        lines.append(f"Nombre de la propuesta: {proposal.name}")
        lines.append(f"Costo total: {proposal.total_cost}")
        lines.append(f"Costo por unidad: {proposal.per_unit_cost}")
        lines.append(f"Ocasión: {proposal.occasion or 'no especificada'}")
        lines.append(
            f"Público objetivo: {proposal.target_audience or 'general'}"
        )

        lines.append("Productos incluidos:")
        for item in proposal.items:
            benefit = (item.name or "").strip()
            lines.append(
                f"- Referencia {item.reference}: {item.name} "
                f"({item.quantity} unidades, {item.unit_price} por unidad). "
                f"Beneficio: {benefit}"
            )

        if proposal.warnings:
            lines.append("Advertencias:")
            for warning in proposal.warnings:
                lines.append(f"- {warning}")

        return "\n".join(lines)

    def build_refinement(
        self,
        proposal: CommercialProposal,
        parent: CommercialProposal,
        log: list,
    ) -> str:
        lines = []
        lines.append("INSTRUCCION: se ha REFINADO una propuesta existente.")
        lines.append(
            "No redactes la propuesta completa desde cero. Explica UNICAMENTE "
            "lo que cambio respecto a la version anterior."
        )
        lines.append(
            f"Version actual: {proposal.version} (padre: v{parent.version})"
        )

        lines.append("Cambios realizados:")
        for entry in log:
            detail = f"- {entry.action}"
            if entry.affected_product:
                detail += f" | producto afectado: {entry.affected_product}"
            if entry.new_product:
                detail += f" | nuevo producto: {entry.new_product}"
            detail += f" | {entry.result}"
            lines.append(detail)

        lines.append("Productos en la propuesta refinada:")
        for item in proposal.items:
            lines.append(
                f"- {item.name} ({item.quantity} uds, {item.unit_price} c/u, "
                f"rol: {item.role or '—'})"
            )
        lines.append(f"Costo total: {proposal.total_cost}")
        lines.append(f"Costo por unidad: {proposal.per_unit_cost}")
        return "\n".join(lines)
