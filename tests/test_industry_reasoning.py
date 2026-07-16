import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from promotional_gifts.domain.entities.commercial_intent import CommercialIntent
from promotional_gifts.domain.entities.product_knowledge import ProductKnowledge
from promotional_gifts.domain.entities.commercial_proposal import CommercialProposal, ProposalItem
from promotional_gifts.domain.services.budget_plan import BudgetPlan
from promotional_gifts.domain.services.product_selector import ProductSelector
from promotional_gifts.domain.services.industry_knowledge import IndustryKnowledge
from promotional_gifts.domain.services.material_reasoner import material_families, materials_match
from promotional_gifts.domain.services.complementarity import kit_complementarity
from promotional_gifts.domain.services.occasion_matcher import OccasionMatcher
from promotional_gifts.domain.services.commercial_scorer import CommercialScorer
from promotional_gifts.domain.services.negative_filter import NegativeFilter
from promotional_gifts.domain.services.budget_optimizer import BudgetOptimizer
from promotional_gifts.domain.services.pricing_engine import PricingEngine
from promotional_gifts.domain.services.proposal_builder import ProposalBuilder, BuildConfig
from promotional_gifts.domain.services.evaluation.proposal_evaluation_engine import (
    ProposalEvaluationEngine,
)
from promotional_gifts.application.intent_analyzer import IntentAnalyzer
from promotional_gifts.domain.services.generation_mode import GenerationMode
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
    """Catalogo representativo con productos coherentes y 'trampas' de otra industria."""
    return [
        # Arquitectura / oficina / escritorio / bambu
        mk("R1", "Libreta RPET Bamboo", 7000, materials="bambu",
           commercial_tags=["personalizable", "eco"], customization="grabado",
           category="oficina", audience_tags=["arquitectura"]),
        mk("R2", "Set escritorio madera", 12000, materials="madera",
           commercial_tags=["premium"], category="oficina"),
        mk("R3", "Boligrafo ejecutivo", 5000, materials="metal",
           commercial_tags=["personalizable"], customization="tampografia",
           category="escritura"),
        mk("R4", "Organizador planos", 9000, materials="carton",
           commercial_tags=["oficina"], category="oficina"),
        # Tecnologia
        mk("R5", "USB corporate", 8000, commercial_tags=["tecnicos", "utilidad"],
           category="tecnologia"),
        mk("R6", "Cargador inalambrico", 15000, commercial_tags=["gadget"],
           category="tecnologia"),
        mk("R7", "Mouse ergonomico", 11000, commercial_tags=["utilidad"],
           category="tecnologia"),
        # Salud / clinicas
        mk("R8", "Termo acero salud", 9000, materials="acero",
           commercial_tags=["bienestar"], category="hogar"),
        mk("R9", "Libreta bienestar", 6000, commercial_tags=["bienestar"],
           category="oficina"),
        # Educacion
        mk("R10", "Cuaderno estudiante", 4000, commercial_tags=["estudiante"],
           category="oficina"),
        mk("R11", "Mochila escolar", 28000, commercial_tags=["estudiante"],
           category="bolsos"),
        # Finanzas / VIP
        mk("R12", "Agenda ejecutiva cuero", 22000, materials="cuero",
           commercial_tags=["premium", "personalizable"], customization="grabado",
           category="oficina"),
        mk("R13", "Kit ejecutivo lujo", 30000, materials="metal",
           commercial_tags=["premium", "alta gama"], category="otros"),
        # Hotelería
        mk("R14", "Kit bienvenida hotel", 13000, commercial_tags=["bienvenida"],
           category="otros"),
        mk("R15", "Toalla bordada", 9000, commercial_tags=["hotel"],
           category="hogar"),
        # Eventos
        mk("R16", "Bolsa merchandising", 5000, commercial_tags=["merchandising"],
           category="otros"),
        mk("R17", "Gorra evento", 7000, commercial_tags=["evento", "branding"],
           category="otros"),
        # Eco / madera
        mk("R18", "Regalo en madera eco", 10000, materials="madera",
           commercial_tags=["eco", "personalizable"], customization="grabado",
           category="otros"),
        mk("R19", "Botella bambu", 6500, materials="bambu",
           commercial_tags=["eco"], category="hogar"),
        # Maleta ejecutiva
        mk("R20", "Maleta ejecutiva cuero", 35000, materials="cuero",
           commercial_tags=["premium", "viaje"], category="viaje"),
        # --- TRAMPAS de otra industria (deben ser penalizadas/excluidas) ---
        mk("T1", "Bowl para mascotas", 4000, commercial_tags=["mascotas"],
           category="mascotas"),
        mk("T2", "Correa para perro", 6000, commercial_tags=["mascota"],
           category="mascotas"),
        mk("T3", "Juguete infantil", 3000, commercial_tags=["juguete", "infantil"],
           category="juguetes"),
        mk("T4", "Set cocina plástico", 8000, commercial_tags=["cocina"],
           category="hogar"),
    ]


CATALOG = build_catalog()
IK = IndustryKnowledge()


def run(text, **intent_overrides):
    ia = IntentAnalyzer()
    intent = ia.analyze(text)
    for k, v in intent_overrides.items():
        setattr(intent, k, v)
    plan = BudgetOptimizer().optimize(intent, GenerationMode.BALANCED)
    selector = ProductSelector(
        OccasionMatcher(), CommercialScorer(), NegativeFilter([]), IK
    )
    scored = selector.select([(p, 0.6) for p in CATALOG], intent, plan, GenerationMode.BALANCED)
    builder = ProposalBuilder(BuildConfig(mode=GenerationMode.BALANCED))
    proposals = builder.build(scored, intent, plan)
    engine = ProposalEvaluationEngine()
    for p in proposals:
        priced = PricingEngine().price(p, plan)
        priced.score_card = engine.evaluate(priced, intent, plan)
    return intent, scored, proposals


def assert_coherent(industry, proposals, scored):
    assert proposals, f"[{industry}] NO se generaron propuestas (caso fallido)"
    # Industrias para las cuales las trampas (mascotas/juguetes/cocina) deben
    # ser excluidas de las propuestas finales.
    strict_industries = {
        "arquitectura", "tecnologia", "salud", "hospital",
        "financiera", "finanzas", "hoteleria", "eventos",
        "construccion", "ingenieria", "vip",
    }
    if industry in strict_industries:
        trap_refs = {"T1", "T2", "T3", "T4"}
        selected = {it.reference for p in proposals for it in p.items}
        leaked = selected & trap_refs
        assert not leaked, f"[{industry}] productos incompatibles filtrados: {leaked}"
    return True


SCENARIOS = [
    "Necesito regalos para una empresa de arquitectura, evento corporativo, 2000 unidades, 20000 por unidad",
    "Necesito regalos para una empresa de tecnologia, 1500 unidades, 18000 por unidad",
    "Necesito regalos para una clinica, 1000 unidades, 15000 por unidad",
    "Necesito regalos para un colegio, 800 unidades, 12000 por unidad",
    "Necesito regalos para clientes VIP, 500 unidades, 40000 por unidad",
    "Necesito regalos para una constructora, 2000 unidades, 16000 por unidad",
    "Necesito regalos para un banco, 1200 unidades, 25000 por unidad",
    "Necesito regalos para un hotel, 900 unidades, 20000 por unidad",
    "Necesito regalos para un evento corporativo, 3000 unidades, 9000 por unidad",
    "Necesito regalos",
    "Quiero una maleta ejecutiva",
    "Regalos en madera",
    "Regalos ecologicos",
]


def test_industry_knowledge_layer():
    # Arquitectura + madera NO debe traer mascotas.
    assert IK.is_avoided("arquitectura", "bowl para mascotas")
    assert IK.industry_score("arquitectura", "libreta bambu oficina") == 1.0
    assert IK.industry_score("arquitectura", "correa para perro") == 0.0
    print("[OK] Industry Knowledge Layer: prefer/avoid funcionan.")


def test_material_reasoning():
    # madera ~ bambu ~ corcho ~ wood
    assert materials_match("madera", "bambu")
    assert materials_match("corcho", "wood")
    assert "madera" in material_families("rpet bamboo eco wood")
    assert not materials_match("madera", "plastico")
    print("[OK] Material reasoning: familias madera/bambu/corcho/wood equivalentes.")


def test_complementarity():
    kit = [CATALOG[0], CATALOG[2], CATALOG[7]]  # libreta, boligrafo, termo
    score = kit_complementarity(kit)
    assert score > 0.5, score
    print(f"[OK] Complementarity: kit variado score={score:.2f}.")


def test_no_pet_leak_in_architecture():
    intent, scored, proposals = run(
        "empresa de arquitectura evento corporativo 2000 unidades 20000 por unidad"
    )
    assert intent.industry == "arquitectura"
    selected = {it.reference for p in proposals for it in p.items}
    assert not (selected & {"T1", "T2", "T3", "T4"}), selected
    print("[OK] Arquitectura: sin productos de mascotas/juguetes/cocina.")


def test_all_scenarios_produce_proposals():
    failures = []
    for s in SCENARIOS:
        try:
            intent, scored, proposals = run(s)
            assert_coherent(intent.industry or s[:20], proposals, scored)
        except AssertionError as e:
            failures.append(str(e))
    if failures:
        print("FALLOS:")
        for f in failures:
            print("  -", f)
        raise SystemExit(1)
    print(f"[OK] Los {len(SCENARIOS)} escenarios obligatorios generan propuestas coherentes.")


def test_fallback_never_empty():
    # Caso extremo: industria 'clinica' con restriccion eco estricta y pocos eco.
    intent, scored, proposals = run(
        "clinica regalos eco 500 unidades 10000 por unidad", eco=True
    )
    assert proposals, "Fallback no devolvio propuestas"
    print("[OK] Fallback: siempre devuelve propuestas (nunca 'no se encontraron').")


def main():
    test_industry_knowledge_layer()
    test_material_reasoning()
    test_complementarity()
    test_no_pet_leak_in_architecture()
    test_fallback_never_empty()
    test_all_scenarios_produce_proposals()
    print("\nTodos los tests del Vertical Slice 11 pasaron.")


if __name__ == "__main__":
    main()
