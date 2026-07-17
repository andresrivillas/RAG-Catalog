"""Batería de pruebas de aceptación para el motor de recomendaciones.

NO modifica el código del motor. Utiliza el caso de uso real,
serializa el ProposalSet devuelto en un único JSON por caso y lo guarda
en tests/results/ con un nombre descriptivo.

Si una consulta falla, guarda el JSON con el error y diagnóstico para
su análisis posterior.
"""

import datetime
import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT))

from config.settings import settings
from promotional_gifts.application.intent_analyzer import IntentAnalyzer
from promotional_gifts.application.prompt.commercial_writer import CommercialWriter
from promotional_gifts.application.prompt.prompt_context_builder import PromptContextBuilder
from promotional_gifts.application.prompt.prompt_loader import PromptLoader
from promotional_gifts.application.use_cases.generate_proposal import GenerateProposalUseCase
from promotional_gifts.container import build_vector_store
from promotional_gifts.domain.services.generation_mode import GenerationMode


RESULTS_DIR = ROOT / "tests" / "results"


CASES = [
    {
        "id": "test_01_software",
        "name": "Empresa de Software",
        "query": (
            "Necesito 500 regalos para una empresa de software. "
            "Quiero transmitir innovación. "
            "Presupuesto máximo de 60.000 COP por unidad."
        ),
        "mode": GenerationMode.BALANCED,
    },
    {
        "id": "test_02_arquitectura",
        "name": "Arquitectura Premium",
        "query": (
            "Necesito 800 regalos para una firma internacional de arquitectura. "
            "Quiero transmitir innovación, elegancia y sostenibilidad. "
            "Todos deben ser personalizables. "
            "Prefiero bambú, madera o RPET. "
            "No quiero plástico de un solo uso. "
            "Presupuesto máximo de 95.000 COP por unidad."
        ),
        "mode": GenerationMode.PREMIUM,
    },
    {
        "id": "test_03_clinica",
        "name": "Clínica",
        "query": (
            "Necesito 400 regalos para una clínica. "
            "Quiero transmitir bienestar y confianza. "
            "Presupuesto máximo de 45.000 COP por unidad."
        ),
        "mode": GenerationMode.BALANCED,
    },
    {
        "id": "test_04_eco",
        "name": "Campaña Ambiental",
        "query": (
            "Necesito 1.500 regalos para una campaña ambiental. "
            "Todos deben ser ecológicos. "
            "Personalizables. "
            "Presupuesto máximo de 30.000 COP por unidad."
        ),
        "mode": GenerationMode.ECO,
    },
    {
        "id": "test_05_vip",
        "name": "Clientes VIP",
        "query": (
            "Necesito 200 regalos para clientes VIP. "
            "Quiero transmitir exclusividad. "
            "Presupuesto máximo de 180.000 COP por unidad."
        ),
        "mode": GenerationMode.PREMIUM,
    },
    {
        "id": "test_06_presupuesto_bajo",
        "name": "Presupuesto Bajo",
        "query": (
            "Necesito 3.800 regalos de cumpleaños. "
            "Presupuesto máximo de 25.000 COP por unidad."
        ),
        "mode": GenerationMode.BUDGET,
    },
]


def build_use_case(mode: GenerationMode) -> GenerateProposalUseCase:
    return GenerateProposalUseCase(
        intent_analyzer=IntentAnalyzer(),
        vector_store=build_vector_store(),
        top_k=settings.top_k * 10,
        commercial_writer=CommercialWriter(
            llm=__import__(
                "promotional_gifts.infrastructure.llm.ollama_llm", fromlist=["OllamaLLM"]
            ).OllamaLLM(
                host=settings.ollama_host,
                top_p=settings.top_p,
                max_tokens=settings.max_tokens,
            ),
            prompt_loader=PromptLoader(settings.prompts_path),
            context_builder=PromptContextBuilder(),
        ),
        llm_model=settings.ollama_model,
        llm_temperature=settings.ollama_temperature,
        negative_keywords=settings.negative_categories,
        workspace=None,  # No persistir en workspace; guardamos JSON manualmente.
        mode=mode,
    )


def run_case(case: dict) -> dict:
    start = datetime.datetime.now()
    intent = Analyzer().analyze(case["query"])
    request_info = {
        "id": case["id"],
        "name": case["name"],
        "query": case["query"],
        "mode": case["mode"].value,
        "parsed_intent": {
            "quantity": intent.quantity,
            "budget_per_unit": intent.budget_per_unit,
            "budget_total": intent.budget_total,
            "occasion": intent.occasion,
            "target_audience": intent.target_audience,
            "industry": intent.industry,
            "eco": intent.eco,
            "personalizable": intent.personalizable,
            "preferred_categories": list(intent.preferred_categories),
            "preferred_materials": list(intent.preferred_materials),
            "generation_mode": intent.generation_mode,
        },
    }

    try:
        use_case = build_use_case(case["mode"])
        proposal_set = use_case.execute(case["query"], intent=intent)
        return {
            "request": request_info,
            "generated_at": start.isoformat(timespec="seconds"),
            "finished_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "proposal_set": proposal_set.to_dict(),
        }
    except Exception as exc:
        return {
            "request": request_info,
            "generated_at": start.isoformat(timespec="seconds"),
            "finished_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "error": str(exc),
            "error_type": type(exc).__name__,
            "traceback": traceback.format_exc(),
            "diagnosis": {
                "stage": "generation",
                "message": "La generación falló. Revisar traceback y estado del catálogo/vector store.",
            },
        }


def Analyzer():
    return IntentAnalyzer()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Bateria de aceptacion para el motor de recomendaciones."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RESULTS_DIR,
        help="Directorio donde se guardan los resultados (default: tests/results)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Sobrescribir resultados existentes",
    )
    args = parser.parse_args()

    results_dir: Path = args.output_dir
    results_dir.mkdir(parents=True, exist_ok=True)

    for case in CASES:
        output_path = results_dir / f"{case['id']}.json"
        if output_path.exists() and not args.overwrite:
            print(f"[SKIP] {output_path.name} ya existe; no se sobrescribe.")
            continue

        print(f"[RUN] {case['id']} — {case['name']} ...")
        result = run_case(case)
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)

        if "error" in result:
            print(f"[ERROR] {case['id']} guardado con diagnostico en {output_path.name}")
        else:
            proposals = result["proposal_set"].get("proposals", [])
            print(f"[OK] {case['id']}: {len(proposals)} propuesta(s) guardadas en {output_path.name}")

    print(f"\nResultados en: {results_dir}")


if __name__ == "__main__":
    main()
