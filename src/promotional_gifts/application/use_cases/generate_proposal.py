from typing import List, Optional

from ...domain.entities.commercial_intent import CommercialIntent
from ...domain.entities.commercial_proposal import CommercialProposal
from ...domain.entities.proposal_set import ProposalSet
from ...domain.entities.product_knowledge import ProductKnowledge
from ...domain.ports.intent_analyzer_port import IntentAnalyzerPort
from ...domain.ports.vector_store_port import VectorStorePort
from ...domain.ports.llm_port import LLMPort
from ...domain.services.budget_optimizer import BudgetOptimizer
from ...domain.services.commercial_scorer import CommercialScorer
from ...domain.services.negative_filter import NegativeFilter
from ...domain.services.occasion_matcher import OccasionMatcher
from ...domain.services.pricing_engine import PricingEngine
from ...domain.services.product_selector import ProductSelector, ScoredProduct
from ...domain.services.proposal_builder import ProposalBuilder, BuildConfig
from ...domain.services.proposal_ranker import ProposalRanker
from ...domain.services.diversity_engine import DiversityEngine
from ...domain.services.evaluation.proposal_evaluation_engine import ProposalEvaluationEngine
from ...domain.services.generation_mode import GenerationMode
from ...domain.services.workspace.proposal_workspace import ProposalWorkspace
from ..prompt.commercial_writer import CommercialWriter
from ..prompt.prompt_context_builder import PromptContextBuilder


class GenerateProposalUseCase:
    def __init__(
        self,
        intent_analyzer: IntentAnalyzerPort,
        vector_store: VectorStorePort,
        top_k: int = 50,
        commercial_writer: Optional[CommercialWriter] = None,
        llm_model: str = "llama3.2",
        llm_temperature: float = 0.3,
        negative_keywords: List[str] = None,
        workspace: ProposalWorkspace = None,
        mode: GenerationMode = None,
    ) -> None:
        self.intent_analyzer = intent_analyzer
        self.vector_store = vector_store
        self.top_k = top_k
        self.commercial_writer = commercial_writer
        self._llm_model = llm_model
        self._llm_temperature = llm_temperature
        self.workspace = workspace
        self.budget_optimizer = BudgetOptimizer()
        self.pricing_engine = PricingEngine()
        self.evaluation_engine = ProposalEvaluationEngine()
        self.proposal_builder = ProposalBuilder(BuildConfig(mode=mode))
        self.proposal_ranker = ProposalRanker(
            evaluation_engine=self.evaluation_engine, debug=False
        )
        self.diversity_engine = DiversityEngine(
            similarity_threshold=0.55
        )
        self.negative_keywords = negative_keywords or []
        self.mode = mode or GenerationMode.BALANCED
        self.product_selector = ProductSelector(
            occasion_matcher=OccasionMatcher(),
            commercial_scorer=CommercialScorer(),
            negative_filter=NegativeFilter(self.negative_keywords),
        )

    def execute(
        self,
        text: str,
        intent: Optional[CommercialIntent] = None,
        plan=None,
    ) -> ProposalSet:
        if intent is None:
            intent = self.intent_analyzer.analyze(text)
        if self.mode is not None:
            intent.generation_mode = self.mode.value

        plan = plan or self.budget_optimizer.optimize(intent, self.mode)

        # 1) Recuperacion compartida (un solo acceso a Chroma para todo el set).
        scored = self._retrieve_and_select(text, intent, plan)

        # 2) Construccion global del set con estrategias distintas.
        proposal_set = self.proposal_builder.build_set(scored, intent, plan)

        if not proposal_set.proposals:
            return proposal_set

        # 3) Precio + evaluacion de cada propuesta, luego ranking global.
        self._price_and_evaluate(proposal_set, intent, plan)
        self._rank(proposal_set)

        # 4) Bucle de diversidad: reconstruir la peor propuesta si es demasiado
        #    similar a otra, usando blacklist dinamica de productos ya usados.
        proposal_set = self._enforce_diversity(proposal_set, intent, plan, scored)

        # 5) Comparacion entre propuestas + estadisticas finales.
        proposal_set.statistics = self.proposal_builder._compute_statistics(proposal_set)
        proposal_set.reused_products = (
            proposal_set.statistics.reused_references if proposal_set.statistics else []
        )
        proposal_set.global_observations = self._global_observations(proposal_set, intent)

        # 6) Validacion final automatica antes de devolver el set.
        proposal_set = self._final_validation(proposal_set, intent, plan)

        # 7) Una unica llamada al LLM con todo el set en contexto.
        if self.commercial_writer:
            self.commercial_writer.write_set(
                proposal_set,
                model=self._llm_model,
                temperature=self._llm_temperature,
            )

        # 8) Persistencia: cada propuesta del set se guarda compartiendo un
        #    root id para poder comparar versiones mas adelante.
        if self.workspace:
            self._persist_set(proposal_set, text, intent)

        return proposal_set

    def _persist_set(
        self, proposal_set: ProposalSet, text: str, intent: CommercialIntent
    ) -> None:
        import datetime
        import uuid

        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        root = f"prop-{stamp}-{uuid.uuid4().hex[:4]}"
        for index, proposal in enumerate(proposal_set.proposals, start=1):
            if not proposal.proposal_id:
                proposal.proposal_id = f"{root}__v{index}"
            self.workspace.create_document(
                proposal=proposal,
                intent=intent,
                original_query=text,
                score_card=proposal.score_card,
                client="",
            )

    # ------------------------------------------------------------------

    def _retrieve_and_select(
        self, text: str, intent: CommercialIntent, plan
    ) -> List[ScoredProduct]:
        relaxed = False
        pool = self._retrieve_with_feedback(text, intent, self.top_k)
        if not pool:
            relaxed = True
            pool = self._retrieve_with_feedback(text, intent, self.top_k * 2)

        scored = self.product_selector.select(pool, intent, plan, self.mode)

        # Fallback inteligente: si la seleccion queda vacia, se relaja el
        # filtro negativo y la restriccion de ocasion.
        if not scored:
            relaxed = True
            scored = self._relax_and_select(pool, intent, plan)

        if relaxed and scored:
            for sp in scored:
                if sp.trace:
                    sp.trace.reason += " (se relajaron restricciones para asegurar propuestas)"
        return scored

    def _retrieve_with_feedback(
        self, text: str, intent: CommercialIntent, top_k: int
    ) -> List[tuple]:
        # Expande la consulta con el contexto comercial del intent.
        query = self._expand_query(text, intent)
        pool = self.vector_store.search(query=query, top_k=top_k)
        if not pool and text:
            pool = self.vector_store.search(query=text, top_k=top_k)
        return pool

    def _expand_query(self, text: str, intent: CommercialIntent) -> str:
        try:
            from ..services.query_expander import expand_query
        except Exception:
            return text
        parts = [text]
        if intent.occasion:
            parts.append(intent.occasion)
        if intent.target_audience:
            parts.append(intent.target_audience)
        if intent.industry:
            parts.append(intent.industry)
        expanded = expand_query(" ".join(p for p in parts if p))
        return expanded or text

    def _relax_and_select(
        self, pool, intent: CommercialIntent, plan
    ) -> List[ScoredProduct]:
        relaxed_intent = CommercialIntent(
            raw_text=intent.raw_text,
            quantity=intent.quantity,
            budget_total=intent.budget_total,
            budget_per_unit=intent.budget_per_unit,
            eco=False,
            personalizable=False,
            packaging_required=False,
            generation_mode=intent.generation_mode,
            industry=intent.industry,
            commercial_context_tags=[],
            segment_tags=[],
        )
        relaxed_selector = ProductSelector(
            occasion_matcher=OccasionMatcher(),
            commercial_scorer=CommercialScorer(),
            negative_filter=NegativeFilter([]),
        )
        return relaxed_selector.select(pool, relaxed_intent, plan, self.mode)

    def _price_and_evaluate(
        self, proposal_set: ProposalSet, intent: CommercialIntent, plan
    ) -> None:
        for proposal in proposal_set.proposals:
            self.pricing_engine.price(proposal, plan)
            card = self.evaluation_engine.evaluate(proposal, intent, plan)
            proposal.score_card = card
            proposal.score = card.overall_score

    def _rank(self, proposal_set: ProposalSet) -> None:
        proposals = proposal_set.proposals
        proposals.sort(key=lambda p: p.score, reverse=True)
        for index, proposal in enumerate(proposals, start=1):
            proposal.name = f"PROPUESTA {index}"

    def _enforce_diversity(
        self,
        proposal_set: ProposalSet,
        intent: CommercialIntent,
        plan,
        scored: List[ScoredProduct],
    ) -> ProposalSet:
        max_iterations = 3
        for _ in range(max_iterations):
            scores = [p.score for p in proposal_set.proposals]
            need = self.diversity_engine.needs_rebuild(proposal_set.proposals, scores)
            if need is None:
                break
            worst_idx, _, sim = need
            blacklist = self.diversity_engine.blacklist_from(
                proposal_set.proposals, worst_idx
            )
            # Reconstruye la propuesta peor usando el pool re-ordenado y la
            # blacklist dinamica (penaliza, no elimina, los productos ya usados).
            proposal_set.proposals[worst_idx] = self._rebuild_one(
                worst_idx, proposal_set, intent, plan, scored, blacklist
            )
            # Reevaluar y re-rankear el set.
            self._price_and_evaluate(proposal_set, intent, plan)
            self._rank(proposal_set)
        return proposal_set

    def _rebuild_one(
        self,
        worst_idx: int,
        proposal_set: ProposalSet,
        intent: CommercialIntent,
        plan,
        scored: List[ScoredProduct],
        blacklist: set,
    ) -> CommercialProposal:
        from ...domain.services.kit_builder import KitBuilder, KitBuildConfig
        from ...domain.services.proposal_builder import _BASE_STRATEGIES
        from statistics import median

        strategy = _BASE_STRATEGIES[worst_idx % len(_BASE_STRATEGIES)]
        # Para la reconstruccion por diversidad se excluyen totalmente los
        # productos de las demas propuestas, garantizando un cambio real.
        available = [sp for sp in scored if sp.product.reference not in blacklist]
        ranked = strategy.rerank(available, intent, plan)
        price_median = median([sp.product.price.amount for sp in ranked]) if ranked else 0.0
        kit_builder = KitBuilder(
            KitBuildConfig(
                num_kits=1,
                min_lines=self.proposal_builder.config.min_lines,
                max_lines=self.proposal_builder.config.max_lines,
                price_median=price_median,
                mode=strategy.generation_mode,
                concept=strategy.label,
            )
        )
        kits = kit_builder.build(intent, ranked, plan)
        proposal = CommercialProposal(name="", score=0.0)
        proposal.generation_mode = strategy.generation_mode.value
        if kits:
            for line in kits[0]:
                item = CommercialProposalItem_from_line(line)
                item.quantity = plan.quantity
                proposal.items.append(item)
        return proposal

    def _global_observations(
        self, proposal_set: ProposalSet, intent: CommercialIntent
    ) -> List[str]:
        obs: List[str] = []
        stats = proposal_set.statistics
        if stats is None:
            return obs
        obs.append(
            f"Set global de {stats.total_proposals} propuestas con "
            f"{stats.category_coverage} categorias distintas cubiertas."
        )
        if stats.reused_products:
            obs.append(
                f"{stats.reused_products} producto(s) reutilizado(s) entre propuestas: "
                f"{', '.join(stats.reused_references)}."
            )
        if stats.shared_product_count:
            obs.append(
                f"{stats.shared_product_count} producto(s) compartido(s) en todas las propuestas: "
                f"{', '.join(stats.shared_references)}."
            )
        obs.append(
            f"Similitud maxima entre propuestas: {stats.max_similarity:.0%}."
        )
        return obs

    def _final_validation(
        self, proposal_set: ProposalSet, intent: CommercialIntent, plan
    ) -> ProposalSet:
        warnings: List[str] = []
        for proposal in proposal_set.proposals:
            # Validacion de presupuesto.
            if plan.spendable_budget > 0 and proposal.total_cost.amount > plan.spendable_budget * 1.05:
                warnings.append(
                    f"{proposal.name}: supera el presupuesto usable en "
                    f"{(proposal.total_cost.amount / plan.spendable_budget - 1) * 100:.0f}%."
                )
            # Validacion de coherencia minima (kit con pocos productos).
            if len(proposal.items) < 3:
                warnings.append(
                    f"{proposal.name}: kit con pocos productos ({len(proposal.items)})."
                )
        if proposal_set.statistics is not None:
            proposal_set.statistics.warnings.extend(warnings)
        return proposal_set


def CommercialProposalItem_from_line(line):
    from ...domain.entities.commercial_proposal import ProposalItem

    return ProposalItem(
        reference=line.product.reference,
        name=line.product.name,
        unit_price=line.product.price,
        quantity=0,  # se ajusta luego por el pricing engine / plan
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
