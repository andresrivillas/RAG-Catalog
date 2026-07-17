from dataclasses import dataclass, field
from statistics import median
from typing import Callable, List, Optional, Tuple

from ..entities.commercial_intent import CommercialIntent
from ..entities.commercial_proposal import CommercialProposal, ProposalItem
from ..entities.product_knowledge import ProductKnowledge
from ..services.budget_plan import BudgetPlan
from ..services.generation_mode import GenerationMode, get_profile
from ..entities.proposal_set import ProposalSet, ProposalSetStatistics
from ..services.kit_builder import KitBuilder, KitBuildConfig
from ..services.product_selector import ScoredProduct
from ..services.proposal_strategy_config import (
    BASE_STRATEGIES as _BASE_STRATEGIES,
    StrategySpec,
    strategies_for,
)
from ..services.diversity_engine import DiversityEngine


@dataclass
class BuildConfig:
    num_proposals: int = 3
    min_lines: int = 5
    max_lines: int = 6
    min_units_per_item: int = 1
    mode: Optional[GenerationMode] = None
    similarity_threshold: float = 0.55


def _score(sp: ScoredProduct) -> float:
    return sp.trace.final_score if sp.trace else sp.score


def _strategies_for(config: BuildConfig, intent: CommercialIntent) -> List[StrategySpec]:
    """Selecciona estrategias tematicas distintas segun la industria y modo.

    La configuracion concreta vive en `proposal_strategy_config` para que
    sea facil de mantener y extender sin tocar el builder.
    """
    return strategies_for(
        intent.industry,
        num_proposals=config.num_proposals,
        mode=config.mode or GenerationMode.BALANCED,
    )


class ProposalBuilder:
    def __init__(self, config: BuildConfig = None) -> None:
        self.config = config or BuildConfig()
        self.diversity_engine = DiversityEngine(
            similarity_threshold=self.config.similarity_threshold
        )

    def build(
        self,
        scored: List[ScoredProduct],
        intent: CommercialIntent,
        plan: BudgetPlan,
    ) -> List[CommercialProposal]:
        # Mantiene compatibilidad: devuelve las propuestas del set global.
        proposal_set = self.build_set(scored, intent, plan)
        return proposal_set.proposals

    def build_set(
        self,
        scored: List[ScoredProduct],
        intent: CommercialIntent,
        plan: BudgetPlan,
    ) -> ProposalSet:
        products: List[ProductKnowledge] = [sp.product for sp in scored]
        if not products:
            return ProposalSet(
                intent=intent,
                budget_plan=plan,
                proposal_count=0,
                proposals=[],
                generation_strategy="global_diversity",
                statistics=ProposalSetStatistics(),
            )

        price_median = median([p.price.amount for p in products]) if products else 0.0
        strategies = _strategies_for(self.config, intent)

        proposals: List[CommercialProposal] = []
        used_refs: set = set()
        reused: List[str] = []

        for idx, strategy in enumerate(strategies):
            # Blacklist dinamica: los productos ya usados en propuestas previas
            # del set se penalizan (no se eliminan) bajando su prioridad.
            # Se aplica ANTES de reranquear para que cada estrategia opere sobre
            # un pool ya penalizado y produzca anclas distintas.
            blacklist = set(used_refs)
            penalized = self._apply_blacklist(scored, blacklist)
            ranked = strategy.rerank(penalized, intent, plan)
            if not ranked:
                continue

            profile = get_profile(strategy.generation_mode)
            kit_builder = KitBuilder(
                KitBuildConfig(
                    num_kits=1,
                    min_lines=profile.min_lines,
                    max_lines=profile.max_lines,
                    price_median=price_median,
                    mode=strategy.generation_mode,
                )
            )
            # KitBuilder.build espera la lista completa; construimos 1 kit.
            kits = kit_builder.build(intent, ranked, plan)
            if not kits:
                continue
            kit = kits[0]

            proposal = CommercialProposal(name="", score=0.0)
            proposal.generation_mode = strategy.generation_mode.value
            local_refs = set()
            for line in kit:
                ref = line.product.reference
                if ref in local_refs:
                    continue
                if ref in used_refs and ref not in reused:
                    reused.append(ref)
                local_refs.add(ref)
                used_refs.add(ref)
                proposal.items.append(
                    ProposalItem(
                        reference=ref,
                        name=line.product.name,
                        unit_price=line.product.price,
                        quantity=plan.quantity,
                        role=line.role,
                        selection_reason=line.reason,
                        decision_trace=line.trace,
                        thumbnail_url=line.product.thumbnail_url or line.product.image_url,
                        detail_url=line.product.detail_url or line.product.url,
                        category=line.product.category,
                        materials=line.product.materials,
                        colors=line.product.colors,
                        capacity=line.product.capacity,
                        customization=line.product.customization,
                        eco="eco" in (line.product.commercial_tags or []),
                        personalizable="personalizable" in (line.product.commercial_tags or []),
                        perceived_value_level=line.product.perceived_value_level,
                    )
                )
            if proposal.items:
                proposals.append(proposal)

        proposal_set = ProposalSet(
            intent=intent,
            budget_plan=plan,
            proposal_count=len(proposals),
            proposals=proposals,
            generation_strategy="global_diversity",
            reused_products=reused,
        )
        proposal_set.statistics = self._compute_statistics(proposal_set)
        return proposal_set

    def _apply_blacklist(
        self, ranked: List[ScoredProduct], blacklist: set
    ) -> List[ScoredProduct]:
        if not blacklist:
            return ranked

        def sort_key(sp: ScoredProduct):
            penalty = 0.85 if sp.product.reference in blacklist else 1.0
            return _score(sp) * penalty

        return sorted(ranked, key=sort_key, reverse=True)

    def _compute_statistics(self, proposal_set: ProposalSet) -> ProposalSetStatistics:
        proposals = proposal_set.proposals
        stats = ProposalSetStatistics(
            total_proposals=len(proposals),
            total_products_considered=len(
                {it.reference for p in proposals for it in p.items}
            ),
        )
        if not proposals:
            return stats

        all_refs: List[str] = []
        for p in proposals:
            all_refs.extend(it.reference for it in p.items)
        ref_counts: dict = {}
        for r in all_refs:
            ref_counts[r] = ref_counts.get(r, 0) + 1
        reused_refs = [r for r, c in ref_counts.items() if c > 1]
        unique = len(ref_counts)
        stats.reused_references = reused_refs
        stats.reused_products = len(reused_refs)
        stats.unique_products_used = unique
        stats.reuse_ratio = (len(reused_refs) / unique) if unique else 0.0

        # Productos compartidos entre TODAS las propuestas.
        sets = [{it.reference for it in p.items} for p in proposals]
        shared = set.intersection(*sets) if sets else set()
        stats.shared_references = list(shared)
        stats.shared_product_count = len(shared)
        total_items = len(all_refs)
        stats.shared_product_ratio = (len(shared) * len(proposals) / total_items) if total_items else 0.0

        cats: set = set()
        for p in proposals:
            for it in p.items:
                if it.category:
                    cats.add(it.category.lower())
        stats.category_list = sorted(cats)
        stats.category_coverage = len(cats)

        # Similitud global.
        stats.max_similarity = self.diversity_engine.max_similarity(proposals)
        if len(proposals) >= 2:
            sims = []
            for i in range(len(proposals)):
                for j in range(i + 1, len(proposals)):
                    sims.append(self.diversity_engine.compare(proposals[i], proposals[j]))
            stats.avg_similarity = sum(sims) / len(sims) if sims else 0.0
        else:
            stats.avg_similarity = 0.0

        # Utilizacion de presupuesto.
        utils = []
        for p in proposals:
            if proposal_set.budget_plan.spendable_budget > 0:
                utils.append(
                    p.total_cost.amount / proposal_set.budget_plan.spendable_budget * 100
                )
        if utils:
            stats.budget_utilization_min = min(utils)
            stats.budget_utilization_max = max(utils)
            stats.budget_utilization_avg = sum(utils) / len(utils)

        if stats.max_similarity >= self.config.similarity_threshold:
            stats.warnings.append(
                "Alta similitud entre propuestas; considera regenerar el set."
            )
        if stats.reuse_ratio > 0.5:
            stats.warnings.append(
                "Alto uso de productos reutilizados entre propuestas."
            )
        return stats
