from dataclasses import dataclass, field
from statistics import median
from typing import Callable, List, Optional, Tuple

from ..entities.commercial_intent import CommercialIntent
from ..entities.commercial_proposal import CommercialProposal, ProposalItem
from ..entities.product_knowledge import ProductKnowledge
from ..services.budget_plan import BudgetPlan
from ..services.generation_mode import GenerationMode
from ..entities.proposal_set import ProposalSet, ProposalSetStatistics
from ..services.kit_builder import KitBuilder, KitBuildConfig
from ..services.product_selector import ScoredProduct
from ..services.diversity_engine import DiversityEngine


@dataclass
class BuildConfig:
    num_proposals: int = 3
    min_lines: int = 5
    max_lines: int = 6
    min_units_per_item: int = 1
    mode: Optional[GenerationMode] = None
    similarity_threshold: float = 0.55


# Una estrategia reordena el pool compartido y define el modo de generacion
# para una propuesta concreta del set global.
@dataclass
class StrategySpec:
    strategy_id: str
    label: str
    generation_mode: GenerationMode
    # Reordena el pool compartido segun el foco de la estrategia.
    rerank: Callable[[List[ScoredProduct], CommercialIntent, BudgetPlan], List[ScoredProduct]]


def _score(sp: ScoredProduct) -> float:
    return sp.trace.final_score if sp.trace else sp.score


def _make_thematic_rerank(category_boost: List[str], tag_boost: List[str], material_boost: List[str]):
    """Devuelve una funcion de reranqueo que prioriza productos de ciertas
    categorias, tags y materiales, manteniendo el score comercial como
    desempate. Asi cada propuesta del set representa una estrategia distinta.
    """
    categories = {c.lower() for c in category_boost}
    tags = {t.lower() for t in tag_boost}
    materials = {m.lower() for m in material_boost}

    def rerank(pool, intent, plan):
        def thematic_score(sp: ScoredProduct) -> float:
            product = sp.product
            score = 0.0
            if (product.category or "").lower() in categories:
                score += 3.0
            product_tags = {t.lower() for t in (product.commercial_tags or [])}
            product_tags |= {t.lower() for t in (product.audience_tags or [])}
            product_tags |= {t.lower() for t in (product.occasion_tags or [])}
            tag_hits = len(product_tags & tags)
            score += tag_hits * 1.5
            product_materials = {
                m.lower()
                for m in (product.materials or "").replace(",", " ").replace(";", " ").split()
            }
            material_hits = len(product_materials & materials)
            score += material_hits * 1.0
            return score

        return sorted(
            pool,
            key=lambda sp: (thematic_score(sp), _score(sp), sp.product.price.amount),
            reverse=True,
        )

    return rerank


# Estrategias tematicas deliberadamente distintas. Cada una impulsa un
# conjunto de categorias/tags diferente para garantizar diversidad real.
_STRATEGY_TECHNOLOGY = StrategySpec(
    "technology",
    "Tecnología",
    GenerationMode.BALANCED,
    _make_thematic_rerank(
        category_boost=["tecnologia", "escritura", "oficina"],
        tag_boost=["usb", "cargador", "gadget", "wireless", "auricular", "power bank", "tecnicos", "tecnologia"],
        material_boost=["metal", "aluminio", "silicona", "plastico"],
    ),
)

_STRATEGY_EXECUTIVE = StrategySpec(
    "executive",
    "Ejecutiva",
    GenerationMode.PREMIUM,
    _make_thematic_rerank(
        category_boost=["oficina", "viaje", "escritura", "bolsos"],
        tag_boost=["premium", "ejecutivo", "corporativo", "alta gama", "personalizable", "libreta", "agenda"],
        material_boost=["cuero", "metal", "madera", "aluminio"],
    ),
)

_STRATEGY_ECO = StrategySpec(
    "eco",
    "Eco",
    GenerationMode.ECO,
    _make_thematic_rerank(
        category_boost=["hogar", "oficina", "otros"],
        tag_boost=["eco", "ecologico", "sostenible", "rpet", "reciclado", "bambu"],
        material_boost=["bambu", "madera", "rpet", "reciclado", "algodon"],
    ),
)

_STRATEGY_WELLNESS = StrategySpec(
    "wellness",
    "Bienestar",
    GenerationMode.BALANCED,
    _make_thematic_rerank(
        category_boost=["hogar", "viaje", "oficina"],
        tag_boost=["bienestar", "salud", "hidratacion", "termo", "botella", "higiene"],
        material_boost=["acero", "bambu", "aluminio", "vidrio"],
    ),
)

_STRATEGY_EVENT = StrategySpec(
    "event",
    "Evento / Branding",
    GenerationMode.BALANCED,
    _make_thematic_rerank(
        category_boost=["otros", "bolsos", "oficina", "escritura"],
        tag_boost=["evento", "merchandising", "branding", "logo", "welcome", "bolsa"],
        material_boost=["plastico", "carton", "algodon", "metal"],
    ),
)


def _rerank_completeness(pool, intent, plan):
    # Estrategia generica de respaldo: maximiza score comercial por peso,
    # favoreciendo productos que dejan espacio para completar el kit.
    def value(sp: ScoredProduct) -> float:
        price = sp.product.price.amount or 1.0
        room = max(0.0, (plan.per_unit_ceiling or price) - price)
        return (_score(sp) * 1.0) / price + room / 10000.0
    return sorted(pool, key=value, reverse=True)


_STRATEGY_COMPLETENESS = StrategySpec(
    "completeness", "Completitud de kit", GenerationMode.BALANCED, _rerank_completeness
)

_BASE_STRATEGIES: List[StrategySpec] = [
    _STRATEGY_EXECUTIVE,
    _STRATEGY_TECHNOLOGY,
    _STRATEGY_ECO,
]


def _strategies_for(config: BuildConfig, intent: CommercialIntent) -> List[StrategySpec]:
    mode = config.mode or GenerationMode.BALANCED
    industry = (intent.industry or "").lower()

    # Fallback por industria: se intentan tres angulos distintos relevantes.
    if industry in {"software", "tecnologia"}:
        return [_STRATEGY_TECHNOLOGY, _STRATEGY_EXECUTIVE, _STRATEGY_ECO][: config.num_proposals]
    if industry in {"arquitectura", "construccion", "ingenieria", "finanzas"}:
        return [_STRATEGY_EXECUTIVE, _STRATEGY_TECHNOLOGY, _STRATEGY_ECO][: config.num_proposals]
    if industry in {"salud", "hospital", "clinica"}:
        return [_STRATEGY_WELLNESS, _STRATEGY_EXECUTIVE, _STRATEGY_ECO][: config.num_proposals]
    if industry in {"eventos"}:
        return [_STRATEGY_EVENT, _STRATEGY_EXECUTIVE, _STRATEGY_ECO][: config.num_proposals]
    if industry in {"educacion", "universidad", "colegio"}:
        return [_STRATEGY_EXECUTIVE, _STRATEGY_TECHNOLOGY, _STRATEGY_ECO][: config.num_proposals]

    if mode == GenerationMode.ECO:
        return [_STRATEGY_ECO, _STRATEGY_EXECUTIVE, _STRATEGY_TECHNOLOGY][: config.num_proposals]
    if mode == GenerationMode.PREMIUM:
        return [_STRATEGY_EXECUTIVE, _STRATEGY_TECHNOLOGY, _STRATEGY_ECO][: config.num_proposals]
    if mode == GenerationMode.BUDGET:
        return [_STRATEGY_TECHNOLOGY, _STRATEGY_ECO, _STRATEGY_EXECUTIVE][: config.num_proposals]

    return _BASE_STRATEGIES[: config.num_proposals]


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

            kit_builder = KitBuilder(
                KitBuildConfig(
                    num_kits=1,
                    min_lines=self.config.min_lines,
                    max_lines=self.config.max_lines,
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
