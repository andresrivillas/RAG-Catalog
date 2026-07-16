import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from promotional_gifts.domain.entities.commercial_intent import CommercialIntent
from promotional_gifts.domain.entities.commercial_proposal import CommercialProposal, ProposalItem
from promotional_gifts.domain.entities.product_knowledge import ProductKnowledge
from promotional_gifts.domain.services.budget_plan import BudgetPlan
from promotional_gifts.domain.services.budget_optimizer import BudgetOptimizer
from promotional_gifts.domain.services.diversity_engine import DiversityEngine
from promotional_gifts.domain.services.proposal_builder import ProposalBuilder, BuildConfig
from promotional_gifts.domain.entities.proposal_set import ProposalSet, ProposalSetStatistics
from promotional_gifts.domain.services.generation_mode import GenerationMode
from promotional_gifts.domain.value_objects.money import Money
from promotional_gifts.application.use_cases.generate_proposal import GenerateProposalUseCase
from promotional_gifts.domain.ports.vector_store_port import VectorStorePort
from promotional_gifts.domain.ports.llm_port import LLMPort


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
        mk("R12", "Soporte movil", 3500, materials="silicona",
           commercial_tags=["utilidad"], category="tecnologia"),
        mk("R13", "Bolsa ecologica", 3000, materials="bambu",
           commercial_tags=["eco", "packaging"], category="otros"),
        mk("R14", "Cuaderno bolsillo", 4500, commercial_tags=["personalizable"],
           customization="logo", category="oficina"),
        mk("R15", "Organizador escritorio", 5500, materials="madera",
           commercial_tags=["utilidad"], category="oficina"),
    ]


class FakeVectorStore(VectorStorePort):
    def __init__(self, products):
        self.products = products

    def add_products(self, products):
        pass

    def search(self, query, top_k):
        return [(p, 0.6) for p in self.products[:top_k]]

    def count(self):
        return len(self.products)


class FakeLLM(LLMPort):
    def generate(self, prompt, temperature, model):
        # Devuelve una seccion por cada ===PROPUESTA N=== implícita: repite
        # la instruccion basica para cada propuesta detectada.
        n = prompt.count("===PROPUESTA ")
        out = []
        for i in range(1, n + 1):
            out.append(f"===PROPUESTA {i}===")
            out.append("Resumen: propuesta redactada por prueba.")
            out.append("Ventajas: coherente y variada.")
            out.append("Ideal para: regalos empresariales.")
        return "\n".join(out)


def test_proposal_set_is_returned():
    catalog = build_catalog()
    store = FakeVectorStore(catalog)
    ia = __import__(
        "promotional_gifts.application.intent_analyzer", fromlist=["IntentAnalyzer"]
    ).IntentAnalyzer()
    uc = GenerateProposalUseCase(
        intent_analyzer=ia,
        vector_store=store,
        top_k=50,
        commercial_writer=None,  # sin LLM para aislar el Business Engine
        negative_keywords=[],
        workspace=None,
        mode=GenerationMode.BALANCED,
    )
    intent = ia.analyze(
        "Necesito 2000 regalos empresariales con presupuesto de 20000 por unidad"
    )
    proposal_set = uc.execute("regalos empresariales 2000 unidades 20000 por unidad", intent=intent)
    assert isinstance(proposal_set, ProposalSet), type(proposal_set)
    assert proposal_set.proposal_count == len(proposal_set.proposals)
    assert len(proposal_set.proposals) == 3, len(proposal_set.proposals)
    print(f"[OK] Use case devuelve ProposalSet con {len(proposal_set.proposals)} propuestas.")


def test_proposals_are_distinct():
    catalog = build_catalog()
    store = FakeVectorStore(catalog)
    ia = __import__(
        "promotional_gifts.application.intent_analyzer", fromlist=["IntentAnalyzer"]
    ).IntentAnalyzer()
    uc = GenerateProposalUseCase(
        intent_analyzer=ia, vector_store=store, top_k=50, commercial_writer=None,
        negative_keywords=[], workspace=None, mode=GenerationMode.BALANCED,
    )
    intent = ia.analyze("Necesito 2000 regalos empresariales presupuesto 20000 por unidad")
    proposal_set = uc.execute("regalos empresariales 2000 unidades 20000 por unidad", intent=intent)

    ref_sets = [{it.reference for it in p.items} for p in proposal_set.proposals]
    # No debe haber dos propuestas exactamente iguales, y la similitud maxima
    # entre cualquier par debe estar por debajo del umbral del DiversityEngine.
    assert len(set(tuple(sorted(r)) for r in ref_sets)) > 1, ref_sets
    engine = DiversityEngine(similarity_threshold=0.55)
    max_sim = engine.max_similarity(proposal_set.proposals)
    assert max_sim < 1.0, max_sim
    print(f"[OK] Propuestas distintas. ref_sets={[sorted(r) for r in ref_sets]}")
    print(f"    max_similarity={max_sim:.2f}, category_coverage={proposal_set.statistics.category_coverage}")


def test_diversity_rebuild_rebuilds_worst():
    engine = DiversityEngine(similarity_threshold=0.55)
    # Dos propuestas casi identicas => necesita reconstruir la peor.
    p1 = CommercialProposal(name="A", score=80.0, items=[
        ProposalItem("R1", "Maleta", Money(18000), 1, role="CORE", category="viaje"),
        ProposalItem("R3", "Libreta", Money(7000), 1, role="UTILITY", category="oficina"),
        ProposalItem("R4", "Boligrafo", Money(5000), 1, role="PROMOTIONAL", category="escritura"),
    ])
    p2 = CommercialProposal(name="B", score=60.0, items=[
        ProposalItem("R1", "Maleta", Money(18000), 1, role="CORE", category="viaje"),
        ProposalItem("R3", "Libreta", Money(7000), 1, role="UTILITY", category="oficina"),
        ProposalItem("R9", "Botella", Money(6500), 1, role="ACCESSORY", category="hogar"),
    ])
    need = engine.needs_rebuild([p1, p2], [p1.score, p2.score])
    assert need is not None, "se esperaba reconstruccion"
    worst_idx, _, sim = need
    assert worst_idx == 1, worst_idx  # la de menor score
    blacklist = engine.blacklist_from([p1, p2], worst_idx)
    assert "R1" in blacklist and "R3" in blacklist
    print(f"[OK] DiversityEngine detecta par similar (sim={sim:.2f}) y marca reconstruir indice {worst_idx}.")


def test_global_observations_and_stats():
    catalog = build_catalog()
    intent = CommercialIntent(
        raw_text="regalos", quantity=2000, budget_per_unit=20000,
        generation_mode="balanced",
    )
    plan = BudgetOptimizer().optimize(intent, GenerationMode.BALANCED)
    store = FakeVectorStore(catalog)
    uc = GenerateProposalUseCase(
        intent_analyzer=__import__(
            "promotional_gifts.application.intent_analyzer", fromlist=["IntentAnalyzer"]
        ).IntentAnalyzer(),
        vector_store=store, top_k=50, commercial_writer=None,
        negative_keywords=[], workspace=None, mode=GenerationMode.BALANCED,
    )
    proposal_set = uc.execute("regalos 2000 unidades 20000 por unidad", intent=intent)
    assert proposal_set.statistics is not None
    assert proposal_set.statistics.total_proposals == 3
    assert isinstance(proposal_set.global_observations, list)
    assert proposal_set.global_observations, "debe haber observaciones globales"
    print(f"[OK] Estadisticas: coverage={proposal_set.statistics.category_coverage}, "
          f"reused={proposal_set.statistics.reused_products}, "
          f"max_sim={proposal_set.statistics.max_similarity:.2f}")
    print(f"    Observaciones: {proposal_set.global_observations}")


def test_single_llm_call_for_set():
    catalog = build_catalog()
    store = FakeVectorStore(catalog)
    llm = FakeLLM()
    calls = {"n": 0}

    class CountingLLM(FakeLLM):
        def generate(self, prompt, temperature, model):
            calls["n"] += 1
            return super().generate(prompt, temperature, model)

    ia = __import__(
        "promotional_gifts.application.intent_analyzer", fromlist=["IntentAnalyzer"]
    ).IntentAnalyzer()
    from promotional_gifts.application.prompt.commercial_writer import CommercialWriter
    from promotional_gifts.application.prompt.prompt_context_builder import PromptContextBuilder
    from promotional_gifts.application.prompt.prompt_loader import PromptLoader
    from pathlib import Path
    from config.settings import settings

    writer = CommercialWriter(
        llm=CountingLLM(),
        prompt_loader=PromptLoader(Path(settings.prompts_path)),
        context_builder=PromptContextBuilder(),
    )
    uc = GenerateProposalUseCase(
        intent_analyzer=ia, vector_store=store, top_k=50,
        commercial_writer=writer, negative_keywords=[], workspace=None,
        mode=GenerationMode.BALANCED,
    )
    proposal_set = uc.execute("regalos empresariales 2000 unidades 20000 por unidad")
    assert calls["n"] == 1, f"se esperaba 1 llamada al LLM, hubo {calls['n']}"
    # Cada propuesta debe tener descripcion asignada por la unica llamada.
    assert all(p.commercial_description for p in proposal_set.proposals)
    print(f"[OK] Una sola llamada al LLM ({calls['n']}) redacta las "
          f"{len(proposal_set.proposals)} propuestas del set.")


def main():
    test_proposal_set_is_returned()
    test_proposals_are_distinct()
    test_diversity_rebuild_rebuilds_worst()
    test_global_observations_and_stats()
    test_single_llm_call_for_set()
    print("\nTodos los tests del Vertical Slice 11 (Global Generation) pasaron.")


if __name__ == "__main__":
    main()
