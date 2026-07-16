from ...domain.entities.commercial_proposal import CommercialProposal
from ...domain.entities.proposal_set import ProposalSet
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

    def build_set(self, proposal_set: ProposalSet) -> str:
        """Construye UN unico contexto con las N propuestas del set en orden,
        de modo que el LLM reciba toda la informacion en una sola llamada.
        """
        intent = proposal_set.intent
        plan = proposal_set.budget_plan
        lines = []
        lines.append("CONTEXTO GLOBAL DE LA SOLICITUD")
        if intent.occasion:
            lines.append(f"- Ocasión: {intent.occasion}")
        if intent.target_audience:
            lines.append(f"- Público objetivo: {intent.target_audience}")
        if intent.industry:
            lines.append(f"- Industria: {intent.industry}")
        lines.append(f"- Cantidad: {plan.quantity}")
        lines.append(
            f"- Presupuesto máximo por unidad: {plan.per_unit_ceiling:,.0f} COP"
        )
        lines.append(
            f"- Presupuesto usable total: {plan.spendable_budget:,.0f} COP"
        )
        if intent.eco:
            lines.append("- Restricción: ECO")
        if intent.personalizable:
            lines.append("- Restricción: PERSONALIZABLE")

        if proposal_set.global_observations:
            lines.append("Observaciones globales del Business Engine:")
            for obs in proposal_set.global_observations:
                lines.append(f"- {obs}")

        lines.append("")
        lines.append(
            f"PROPUESTAS A REDACTAR ({proposal_set.proposal_count}). "
            "Redacta UNA sección por propuesta usando exactamente el marcador "
            "===PROPUESTA N=== al inicio de cada una (N = 1, 2, 3...). "
            "En cada sección incluye: Resumen, Ventajas y Ideal para."
        )

        for index, proposal in enumerate(proposal_set.proposals, start=1):
            lines.append("")
            lines.append(f"===PROPUESTA {index}===")
            lines.append(f"Nombre sugerido: {proposal.name}")
            lines.append(f"Modo: {proposal.generation_mode or 'balanced'}")
            lines.append(f"Costo total: {proposal.total_cost}")
            lines.append(f"Costo por unidad: {proposal.per_unit_cost}")
            lines.append("Productos incluidos:")
            for item in proposal.items:
                lines.append(
                    f"- Referencia {item.reference}: {item.name} "
                    f"({item.quantity} unidades, {item.unit_price} por unidad). "
                    f"Rol: {item.role or '—'}. Categoría: {item.category or '—'}."
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
