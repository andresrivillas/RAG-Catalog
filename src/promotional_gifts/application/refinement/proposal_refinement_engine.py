from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from ...domain.entities.commercial_intent import CommercialIntent
from ...domain.entities.commercial_proposal import CommercialProposal, ProposalItem
from ...domain.entities.product_knowledge import ProductKnowledge
from ...domain.entities.proposal_modification_request import ProposalModificationRequest
from ...domain.ports.vector_store_port import VectorStorePort
from ...domain.services.budget_plan import BudgetPlan
from ...domain.services.commercial_scorer import CommercialScorer
from ...domain.services.decision_trace import DecisionTrace
from ...domain.services.negative_filter import NegativeFilter
from ...domain.services.occasion_matcher import OccasionMatcher
from ...domain.services.pricing_engine import PricingEngine
from ...domain.services.product_selector import ProductSelector, ECO_KEYWORDS, PERSONALIZABLE_KEYWORDS


@dataclass
class RefinementLogEntry:
    action: str
    affected_product: str = ""
    new_product: str = ""
    reason: str = ""
    result: str = ""


class ProposalRefinementEngine:
    def __init__(
        self,
        vector_store: VectorStorePort,
        occasion_matcher: OccasionMatcher,
        commercial_scorer: CommercialScorer,
        negative_filter: NegativeFilter,
        pricing_engine: PricingEngine,
        top_k: int = 50,
        negative_keywords: List[str] = None,
    ) -> None:
        self.vector_store = vector_store
        self.occasion_matcher = occasion_matcher
        self.commercial_scorer = commercial_scorer
        self.negative_filter = negative_filter
        self.pricing_engine = pricing_engine
        self.top_k = top_k
        self.product_selector = ProductSelector(
            occasion_matcher=occasion_matcher,
            commercial_scorer=commercial_scorer,
            negative_filter=negative_filter,
        )
        self._selector = self.product_selector

    def refine(
        self,
        proposal: CommercialProposal,
        request: ProposalModificationRequest,
        intent: Optional[CommercialIntent] = None,
        plan: Optional[BudgetPlan] = None,
    ) -> Tuple[CommercialProposal, List[RefinementLogEntry]]:
        log: List[RefinementLogEntry] = []
        new_proposal = proposal.clone_as_refinement()

        if request.action == ProposalModificationRequest.NO_OP:
            log.append(
                RefinementLogEntry(request.action, reason=request.reason, result="Sin cambios")
            )
            return new_proposal, log

        handler = {
            ProposalModificationRequest.REPLACE_PRODUCT: self._replace_product,
            ProposalModificationRequest.REMOVE_PRODUCT: self._remove_product,
            ProposalModificationRequest.ADD_PRODUCT: self._add_product,
            ProposalModificationRequest.CHANGE_BUDGET: self._change_budget,
            ProposalModificationRequest.PREMIUM_UPGRADE: self._premium_upgrade,
            ProposalModificationRequest.BUDGET_REDUCTION: self._budget_reduction,
            ProposalModificationRequest.ECO_ONLY: self._eco_only,
            ProposalModificationRequest.REMOVE_MATERIAL: self._remove_material,
            ProposalModificationRequest.REQUIRE_MATERIAL: self._require_material,
            ProposalModificationRequest.CHANGE_CATEGORY: self._change_category,
            ProposalModificationRequest.REGENERATE_PACKAGING: self._regenerate_packaging,
        }.get(request.action)

        if handler is None:
            log.append(
                RefinementLogEntry(request.action, reason=request.reason, result="Acción no soportada")
            )
            return new_proposal, log

        handler(new_proposal, request, intent, plan, log)

        self.pricing_engine.price(new_proposal, plan or _empty_plan(new_proposal))
        new_proposal.score = self._recalculate_score(new_proposal)
        new_proposal.refinements.append(request.reason)
        return new_proposal, log

    def _find_references(self, query: str) -> List[Tuple[ProductKnowledge, float]]:
        return self.vector_store.search(query=query, top_k=self.top_k)

    def _best_alternative(
        self,
        exclude_refs: set,
        intent: Optional[CommercialIntent],
        plan: Optional[BudgetPlan],
        request: ProposalModificationRequest,
    ) -> Optional[ProductKnowledge]:
        pool = self._find_references(request.new_product or request.old_product or "")
        chosen: Optional[ProductKnowledge] = None
        best_score = -1.0
        for product, _similarity in pool:
            if product.reference in exclude_refs:
                continue
            if product.price.amount <= 0:
                continue
            if self.negative_filter.is_excluded(product):
                continue
            if plan and product.price.amount > plan.per_unit_ceiling:
                continue
            if request.material and request.action == ProposalModificationRequest.REQUIRE_MATERIAL:
                if request.material not in (product.materials or "").lower():
                    continue
            occ = self.occasion_matcher.score(intent, product) if intent else 0.0
            com = self.commercial_scorer.score(intent, product) if intent else 0.0
            val = occ * 0.4 + com / 100 * 0.6
            if val > best_score:
                best_score = val
                chosen = product
        return chosen

    def _to_item(self, product: ProductKnowledge, role: str, qty: int) -> ProposalItem:
        trace = DecisionTrace()
        trace.semantic_score = 0.5
        trace.occasion_score = 0.5
        trace.commercial_score = self.commercial_scorer.score(None, product)
        trace.budget_score = 0.5
        trace.final_score = trace.commercial_score / 100 * 30 + 15
        trace.reason = f"Añadido por refinamiento: {role}."
        return ProposalItem(
            reference=product.reference,
            name=product.name,
            unit_price=product.price,
            quantity=qty,
            role=role,
            selection_reason=trace.reason,
            decision_trace=trace,
            thumbnail_url=product.thumbnail_url or product.image_url,
            detail_url=product.detail_url or product.url,
        )

    def _replace_product(self, proposal, request, intent, plan, log):
        target = self._find_item(proposal, request.old_product)
        if target is None:
            log.append(RefinementLogEntry(request.action, reason=request.reason, result="Producto no encontrado"))
            return
        alternative = self._best_alternative(
            {target.reference}, intent, plan, request
        )
        if alternative is None:
            log.append(RefinementLogEntry(request.action, affected_product=target.name, reason=request.reason, result="Sin alternativa"))
            return
        proposal.items = [
            it for it in proposal.items if it.reference != target.reference
        ]
        proposal.items.append(
            self._to_item(alternative, target.role or "CORE", target.quantity)
        )
        log.append(
            RefinementLogEntry(
                request.action,
                affected_product=target.name,
                new_product=alternative.name,
                reason=request.reason,
                result="Reemplazado",
            )
        )

    def _remove_product(self, proposal, request, intent, plan, log):
        target = self._find_item(proposal, request.old_product)
        if target is None:
            # remove by material instead
            removed = [it for it in proposal.items if request.old_product in (it.name or "").lower()]
            if removed:
                proposal.items = [it for it in proposal.items if it not in removed]
                for r in removed:
                    log.append(RefinementLogEntry(request.action, affected_product=r.name, reason=request.reason, result="Eliminado"))
                return
            log.append(RefinementLogEntry(request.action, reason=request.reason, result="Producto no encontrado"))
            return
        proposal.items = [it for it in proposal.items if it.reference != target.reference]
        log.append(
            RefinementLogEntry(
                request.action,
                affected_product=target.name,
                reason=request.reason,
                result="Eliminado",
            )
        )

    def _add_product(self, proposal, request, intent, plan, log):
        exclude = {it.reference for it in proposal.items}
        alternative = self._best_alternative(exclude, intent, plan, request)
        if alternative is None:
            log.append(RefinementLogEntry(request.action, reason=request.reason, result="Sin alternativa"))
            return
        qty = proposal.items[0].quantity if proposal.items else 1
        proposal.items.append(self._to_item(alternative, "ACCESSORY", qty))
        log.append(
            RefinementLogEntry(
                request.action,
                new_product=alternative.name,
                reason=request.reason,
                result="Añadido",
            )
        )

    def _change_budget(self, proposal, request, intent, plan, log):
        if plan is None:
            log.append(RefinementLogEntry(request.action, reason=request.reason, result="Sin plan de presupuesto"))
            return
        plan.per_unit_ceiling = request.budget_per_unit
        plan.spendable_budget = request.budget_per_unit * plan.quantity
        over = [it for it in proposal.items if it.unit_price.amount > request.budget_per_unit]
        for it in over:
            alternative = self._best_alternative(
                {it.reference} | {x.reference for x in proposal.items},
                intent,
                plan,
                request,
            )
            if alternative:
                proposal.items = [x for x in proposal.items if x.reference != it.reference]
                qty = it.quantity
                proposal.items.append(self._to_item(alternative, it.role or "CORE", qty))
                log.append(
                    RefinementLogEntry(
                        request.action,
                        affected_product=it.name,
                        new_product=alternative.name,
                        reason=f"Ajustado a presupuesto {request.budget_per_unit:,.0f}",
                        result="Sustituido",
                    )
                )
            else:
                log.append(
                    RefinementLogEntry(
                        request.action,
                        affected_product=it.name,
                        reason=request.reason,
                        result="Sin alternativa dentro del presupuesto",
                    )
                )

    def _premium_upgrade(self, proposal, request, intent, plan, log):
        for it in proposal.items:
            alternative = self._best_alternative(
                {it.reference}, intent, plan, request
            )
            if alternative and alternative.price.amount > it.unit_price.amount:
                proposal.items = [x for x in proposal.items if x.reference != it.reference]
                proposal.items.append(self._to_item(alternative, it.role or "CORE", it.quantity))
                log.append(
                    RefinementLogEntry(
                        request.action,
                        affected_product=it.name,
                        new_product=alternative.name,
                        reason=request.reason,
                        result="Mejorado",
                    )
                )

    def _budget_reduction(self, proposal, request, intent, plan, log):
        for it in proposal.items:
            alternative = self._best_alternative(
                {it.reference}, intent, plan, request
            )
            if alternative and alternative.price.amount < it.unit_price.amount:
                proposal.items = [x for x in proposal.items if x.reference != it.reference]
                proposal.items.append(self._to_item(alternative, it.role or "CORE", it.quantity))
                log.append(
                    RefinementLogEntry(
                        request.action,
                        affected_product=it.name,
                        new_product=alternative.name,
                        reason=request.reason,
                        result="Abaratado",
                    )
                )

    def _eco_only(self, proposal, request, intent, plan, log):
        for it in list(proposal.items):
            text = f"{it.name} {it.selection_reason}".lower()
            if not any(kw in text for kw in ECO_KEYWORDS):
                alternative = self._find_eco_alternative(it, intent, plan)
                if alternative:
                    proposal.items = [x for x in proposal.items if x.reference != it.reference]
                    proposal.items.append(self._to_item(alternative, it.role or "CORE", it.quantity))
                    log.append(
                        RefinementLogEntry(
                            request.action,
                            affected_product=it.name,
                            new_product=alternative.name,
                            reason=request.reason,
                            result="Eco",
                        )
                    )
                else:
                    log.append(
                        RefinementLogEntry(
                            request.action,
                            affected_product=it.name,
                            reason=request.reason,
                            result="Sin alternativa eco",
                        )
                    )

    def _find_eco_alternative(self, item, intent, plan):
        pool = self._find_references((item.name or "")[:40])
        for product, _ in pool:
            text = f"{product.name} {product.description} {product.materials}".lower()
            if any(kw in text for kw in ECO_KEYWORDS) and product.price.amount > 0:
                if plan and product.price.amount > plan.per_unit_ceiling:
                    continue
                return product
        return None

    def _remove_material(self, proposal, request, intent, plan, log):
        material = request.material or ""
        for it in list(proposal.items):
            if material in (it.name or "").lower() or material in (it.selection_reason or "").lower():
                alternative = self._best_alternative(
                    {it.reference}, intent, plan, request
                )
                if alternative and material not in (alternative.materials or "").lower():
                    proposal.items = [x for x in proposal.items if x.reference != it.reference]
                    proposal.items.append(self._to_item(alternative, it.role or "CORE", it.quantity))
                    log.append(
                        RefinementLogEntry(
                            request.action,
                            affected_product=it.name,
                            new_product=alternative.name,
                            reason=request.reason,
                            result="Sustituido",
                        )
                    )
                else:
                    proposal.items = [x for x in proposal.items if x.reference != it.reference]
                    log.append(
                        RefinementLogEntry(
                            request.action,
                            affected_product=it.name,
                            reason=request.reason,
                            result="Eliminado (sin alternativa válida)",
                        )
                    )

    def _require_material(self, proposal, request, intent, plan, log):
        material = request.material or ""
        for it in list(proposal.items):
            if material not in (it.name or "").lower() and material not in (it.selection_reason or "").lower():
                alternative = self._best_alternative(
                    {it.reference}, intent, plan, request
                )
                if alternative and material in (alternative.materials or "").lower():
                    proposal.items = [x for x in proposal.items if x.reference != it.reference]
                    proposal.items.append(self._to_item(alternative, it.role or "CORE", it.quantity))
                    log.append(
                        RefinementLogEntry(
                            request.action,
                            affected_product=it.name,
                            new_product=alternative.name,
                            reason=request.reason,
                            result="Sustituido",
                        )
                    )

    def _change_category(self, proposal, request, intent, plan, log):
        for it in list(proposal.items):
            if request.category not in (it.name or "").lower():
                alternative = self._best_alternative(
                    {it.reference}, intent, plan, request
                )
                if alternative:
                    proposal.items = [x for x in proposal.items if x.reference != it.reference]
                    proposal.items.append(self._to_item(alternative, it.role or "CORE", it.quantity))
                    log.append(
                        RefinementLogEntry(
                            request.action,
                            affected_product=it.name,
                            new_product=alternative.name,
                            reason=request.reason,
                            result="Sustituido",
                        )
                    )

    def _regenerate_packaging(self, proposal, request, intent, plan, log):
        if not proposal.items:
            log.append(RefinementLogEntry(request.action, reason=request.reason, result="Sin items"))
            return
        pool = self._find_references("bolsa caja estuche empaque packaging")
        for product, _ in pool:
            if product.reference in {it.reference for it in proposal.items}:
                continue
            if product.price.amount > 0 and self._role_of(product) == "PACKAGING":
                qty = proposal.items[0].quantity
                proposal.items.append(self._to_item(product, "PACKAGING", qty))
                log.append(
                    RefinementLogEntry(
                        request.action,
                        new_product=product.name,
                        reason=request.reason,
                        result="Empaque añadido",
                    )
                )
                return
        log.append(RefinementLogEntry(request.action, reason=request.reason, result="Sin empaque disponible"))

    def _role_of(self, product: ProductKnowledge) -> str:
        from ...domain.services.role_classifier import RoleClassifier
        return RoleClassifier().classify(product, 0.0)

    def _find_item(self, proposal: CommercialProposal, keyword: str) -> Optional[ProposalItem]:
        if not keyword:
            return None
        kw = keyword.lower()
        for it in proposal.items:
            if kw in (it.name or "").lower() or kw in (it.reference or "").lower():
                return it
        return None

    def _recalculate_score(self, proposal: CommercialProposal) -> float:
        if not proposal.items:
            return 0.0
        avg = sum(
            (it.decision_trace.final_score if it.decision_trace else 0.0)
            for it in proposal.items
        ) / len(proposal.items)
        return avg


def _empty_plan(proposal: CommercialProposal) -> BudgetPlan:
    qty = proposal.items[0].quantity if proposal.items else 1
    ceiling = max((it.unit_price.amount for it in proposal.items), default=0.0) * 2
    return BudgetPlan(
        total_budget=0.0,
        spendable_budget=0.0,
        per_unit_ceiling=ceiling,
        margin_reserve=0.0,
        quantity=qty,
    )
