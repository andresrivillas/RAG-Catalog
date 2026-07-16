import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from promotional_gifts.domain.entities.commercial_intent import CommercialIntent
from promotional_gifts.domain.entities.commercial_proposal import CommercialProposal, ProposalItem
from promotional_gifts.domain.entities.product_knowledge import ProductKnowledge
from promotional_gifts.domain.services.budget_plan import BudgetPlan
from promotional_gifts.domain.services.product_selector import ProductSelector
from promotional_gifts.domain.services.kit_builder import KitBuilder, KitBuildConfig
from promotional_gifts.domain.services.proposal_builder import ProposalBuilder, BuildConfig
from promotional_gifts.domain.services.pricing_engine import PricingEngine
from promotional_gifts.domain.services.occasion_matcher import OccasionMatcher
from promotional_gifts.domain.services.commercial_scorer import CommercialScorer
from promotional_gifts.domain.services.negative_filter import NegativeFilter
from promotional_gifts.domain.services.budget_optimizer import BudgetOptimizer
from promotional_gifts.domain.services.evaluation.proposal_evaluation_engine import (
    ProposalEvaluationEngine,
)
from promotional_gifts.application.intent_analyzer import IntentAnalyzer
from promotional_gifts.domain.services.generation_mode import GenerationMode, get_profile
from promotional_gifts.domain.value_objects.money import Money


def mk(ref, name, price, **kw):
    return ProductKnowledge(
        reference=ref,
        name=name,
        price=Money(amount=price, currency="COP"),
        materials=kw.get("materials", ""),
        colors=kw.get("colors", ""),
        capacity=kw.get("capacity", ""),
        customization=kw.get("customization", ""),
        category=kw.get("category", ""),
        commercial_tags=kw.get("commercial_tags", []),
        audience_tags=kw.get("audience_tags", []),
        occasion_tags=kw.get("occasion_tags", []),
        benefits=kw.get("benefits", ""),
        perceived_value_level=kw.get("perceived_value_level", "medio"),
        description=kw.get("description", ""),
    )


def build_catalog():
    return [
        mk("R1", "Maleta ejecutiva de cuero", 18000, materials="cuero",
           commercial_tags=["premium"], category="viaje", audience_tags=["ejecutivo"],
           perceived_value_level="alto"),
        mk("R2", "Mochila laptop", 12000, materials="poliester",
           commercial_tags=["utilidad"], category="bolsos", audience_tags=["ejecutivo"]),
        mk("R3", "Libreta ejecutiva", 7000, materials="papel",
           commercial_tags=["personalizable"], customization="grabado laser",
           category="oficina", audience_tags=["ejecutivo"]),
        mk("R4", "Boligrafo metalico", 5000, materials="metal",
           commercial_tags=["personalizable"], customization="tampografia",
           category="escritura"),
        mk("R5", "Termo acero inoxidable", 9000, materials="acero",
           commercial_tags=["utilidad"], category="hogar", capacity="500 ml"),
        mk("R6", "Caja regalo corporativa", 4000, materials="carton",
           commercial_tags=["packaging"], category="otros"),
        mk("R7", "Paraguas compacto", 8000, materials="aluminio",
           commercial_tags=["utilidad"], category="viaje"),
        mk("R8", "Agenda corporativa", 6000, commercial_tags=["personalizable"],
           customization="logo", category="oficina"),
        mk("R9", "Botella bambu eco", 6500, materials="bambu",
           commercial_tags=["eco", "personalizable"], customization="grabado",
           category="hogar", perceived_value_level="alto"),
        mk("R10", "Set escritorio tecnologia", 11000, materials="silicona",
           commercial_tags=["tecnicos"], category="escritura", audience_tags=["tecnicos"]),
        mk("R11", "Llavero personalizable", 2500, materials="metal",
           commercial_tags=["personalizable", "promocional"], customization="grabado",
           category="otros"),
        mk("R12", "Adhesivo logo", 2000, commercial_tags=["promocional"],
           customization="sublimacion", category="otros"),
        mk("R13", "Pegatinas marca", 2200, commercial_tags=["promocional", "branding"],
           customization="logo", category="otros"),
        mk("R14", "Soporte movil", 3500, materials="silicona",
           commercial_tags=["utilidad"], category="tecnologia"),
        mk("R15", "Bolsa ecologica", 3000, materials="bambu",
           commercial_tags=["eco", "packaging"], category="otros"),
        mk("R16", "Cuaderno bolsillo", 4500, commercial_tags=["personalizable"],
           customization="logo", category="oficina"),
        mk("R17", "Sello mano", 5000, materials="madera",
           commercial_tags=["utilidad"], category="otros"),
        mk("R18", "Organizador escritorio", 5500, materials="madera",
           commercial_tags=["utilidad"], category="oficina"),
    ]


def score(intent, products, mode=GenerationMode.BALANCED):
    plan = BudgetOptimizer().optimize(intent, mode)
    selector = ProductSelector(OccasionMatcher(), CommercialScorer(), NegativeFilter([]))
    scored = selector.select([(p, 0.6) for p in products], intent, plan, mode)
    return scored, plan


def test_intent_enrichment():
    ia = IntentAnalyzer()
    intent = ia.analyze("Necesito 2000 regalos para una empresa de arquitectura, clientes VIP, presupuesto 20000 por unidad")
    assert intent.industry == "arquitectura", intent.industry
    assert "vip" in intent.segment_tags, intent.segment_tags
    assert intent.commercial_context_tags, intent.commercial_context_tags
    print(f"[OK] IntentAnalyzer enriquece: industry={intent.industry}, segmentos={intent.segment_tags}, tags={intent.commercial_context_tags}")


def test_query_expansion():
    from promotional_gifts.domain.services.query_expander import expand_query
    q = expand_query("maleta ejecutiva regalo promocional")
    assert "backpack" in q and "laptop" in q, q
    q2 = expand_query("eco regalo promocional")
    assert "bambu" in q2 and "reciclado" in q2, q2
    print(f"[OK] Query expansion amplia sin reemplazar: '{q}'")


def test_context_match_boost():
    products = build_catalog()
    intent = CommercialIntent(raw_text="arquitectura vip 20000 por unidad", industry="arquitectura",
                              segment_tags=["vip"], commercial_context_tags=["oficina", "ejecutivo", "diseno", "diseño"],
                              quantity=2000, budget_per_unit=20000)
    scored, _ = score(intent, products)
    top = scored[0].product.reference
    # Productos de oficina/ejecutivo deben rankear alto por contexto.
    assert top in {"R3", "R8", "R1", "R2"}, top
    print(f"[OK] Context match: top producto={top} (score {scored[0].score:.1f})")


def test_budget_utilization():
    products = build_catalog()
    intent = CommercialIntent(raw_text="2000 regalos presupuesto 20000 por unidad",
                              quantity=2000, budget_per_unit=20000)
    plan = BudgetOptimizer().optimize(intent, GenerationMode.BALANCED)
    selector = ProductSelector(OccasionMatcher(), CommercialScorer(), NegativeFilter([]))
    scored = selector.select([(p, 0.6) for p in products], intent, plan, GenerationMode.BALANCED)
    builder = ProposalBuilder(BuildConfig(mode=GenerationMode.BALANCED))
    proposals = builder.build(scored, intent, plan)
    engine = ProposalEvaluationEngine()
    utilizations = []
    for p in proposals:
        priced = PricingEngine().price(p, plan)
        card = engine.evaluate(priced, intent, plan)
        priced.score_card = card
        util = priced.total_cost.amount / plan.spendable_budget * 100
        utilizations.append((priced.name, util, priced.score, len(priced.items)))
    for name, util, sc, n in utilizations:
        print(f"   {name}: {n} productos, utilizacion={util:.0f}%, score={sc:.1f}")
    assert utilizations, "no proposals"
    assert max(u for _, u, _, _ in utilizations) >= 85.0, utilizations
    assert all(n >= 4 for _, _, _, n in utilizations), utilizations
    print(f"[OK] Budget utilization alto (>=85%) y kits completos (>=4 productos)")


def test_low_utilization_penalized():
    # Kit de 1 producto barato => utilizacion baja => score bajo en Budget Efficiency.
    from promotional_gifts.domain.services.evaluation.criteria import BudgetEfficiencyCriterion
    items = [ProposalItem(reference="R4", name="Boligrafo", unit_price=Money(5000, "COP"), quantity=100, role="CORE")]
    prop = CommercialProposal(name="P", score=0, items=items)
    plan = BudgetPlan(total_budget=2_000_000, spendable_budget=1_900_000, per_unit_ceiling=20000, margin_reserve=100000, quantity=100)
    prop.total_cost = Money(500_000, "COP")
    c = BudgetEfficiencyCriterion().evaluate(prop, None, plan)
    ratio = 500_000 / 1_900_000
    assert c.score < 60.0, c.score
    print(f"[OK] Subutilizacion penalizada: ratio={ratio*100:.0f}%, score={c.score:.1f}")


def test_kit_coherence_single():
    from promotional_gifts.domain.services.evaluation.criteria import KitCoherenceCriterion
    items = [ProposalItem(reference="R4", name="Boligrafo", unit_price=Money(5000, "COP"), quantity=1, role="CORE")]
    prop = CommercialProposal(name="P", score=0, items=items)
    c = KitCoherenceCriterion().evaluate(prop, None, None)
    assert c.score <= 20.0, c.score
    print(f"[OK] Kit de 1 producto baja coherencia: score={c.score:.1f}")


def main():
    test_intent_enrichment()
    test_query_expansion()
    test_context_match_boost()
    test_budget_utilization()
    test_low_utilization_penalized()
    test_kit_coherence_single()
    print("\nTodos los smoke tests del Business Engine pasaron.")


if __name__ == "__main__":
    main()
