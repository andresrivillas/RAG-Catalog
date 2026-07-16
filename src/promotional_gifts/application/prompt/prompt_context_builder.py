from ...domain.entities.commercial_proposal import CommercialProposal


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
