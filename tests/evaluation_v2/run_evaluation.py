#!/usr/bin/env python3
"""Evaluation v2 - 6 escenarios de prueba. Salida completa del motor sin modificar."""
import json
import sys
import time
from dataclasses import is_dataclass, fields
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from promotional_gifts.container import build_generate_proposal_use_case
from promotional_gifts.domain.entities.commercial_intent import CommercialIntent
from promotional_gifts.domain.entities.commercial_proposal import CommercialProposal, ProposalItem
from promotional_gifts.domain.entities.proposal_set import ProposalSet, ProposalSetStatistics
from promotional_gifts.domain.services.budget_plan import BudgetPlan
from promotional_gifts.domain.services.decision_trace import DecisionTrace
from promotional_gifts.domain.services.evaluation.proposal_score_card import ProposalScoreCard
from promotional_gifts.domain.value_objects.money import Money


def serialize(obj):
    if obj is None:
        return None
    if isinstance(obj, Money):
        return {"amount": obj.amount, "currency": obj.currency}
    if isinstance(obj, DecisionTrace):
        return {
            "semantic_score": obj.semantic_score,
            "commercial_score": obj.commercial_score,
            "occasion_score": obj.occasion_score,
            "budget_score": obj.budget_score,
            "context_score": obj.context_score,
            "industry_score": obj.industry_score,
            "affinity_score": obj.affinity_score,
            "availability_score": obj.availability_score,
            "commercial_value_score": obj.commercial_value_score,
            "harmony_score": obj.harmony_score,
            "final_score": obj.final_score,
            "reason": obj.reason,
            "detail": obj.detail,
        }
    if isinstance(obj, ProposalScoreCard):
        return {
            "overall_score": obj.overall_score,
            "budget_score": obj.budget_score,
            "commercial_score": obj.commercial_score,
            "coherence_score": obj.coherence_score,
            "diversity_score": obj.diversity_score,
            "category_diversity_score": obj.category_diversity_score,
            "utility_score": obj.utility_score,
            "brand_visibility_score": obj.brand_visibility_score,
            "premium_score": obj.premium_score,
            "eco_score": obj.eco_score,
            "personalization_score": obj.personalization_score,
            "occasion_score": obj.occasion_score,
            "audience_score": obj.audience_score,
            "balance_score": obj.balance_score,
            "industry_score": obj.industry_score,
            "complementarity_score": obj.complementarity_score,
            "category_quality_score": obj.category_quality_score,
            "material_cleanliness_score": obj.material_cleanliness_score,
            "mode_coherence_score": obj.mode_coherence_score,
            "availability_score": obj.availability_score,
            "selection_reason_quality_score": obj.selection_reason_quality_score,
            "consistency_score": obj.consistency_score,
            "explainability_score": obj.explainability_score,
            "criteria": [serialize(c) for c in obj.criteria],
            "observations": list(obj.observations),
        }
    if isinstance(obj, ProposalItem):
        return {
            "reference": obj.reference,
            "name": obj.name,
            "unit_price": serialize(obj.unit_price),
            "quantity": obj.quantity,
            "role": obj.role,
            "selection_reason": obj.selection_reason,
            "decision_trace": serialize(obj.decision_trace),
            "thumbnail_url": obj.thumbnail_url,
            "detail_url": obj.detail_url,
            "category": obj.category,
            "materials": obj.materials,
            "colors": obj.colors,
            "capacity": obj.capacity,
            "customization": obj.customization,
            "eco": obj.eco,
            "personalizable": obj.personalizable,
            "perceived_value_level": obj.perceived_value_level,
        }
    if isinstance(obj, CommercialProposal):
        return {
            "name": obj.name,
            "score": obj.score,
            "items": [serialize(i) for i in obj.items],
            "total_cost": serialize(obj.total_cost),
            "per_unit_cost": serialize(obj.per_unit_cost),
            "warnings": list(obj.warnings),
            "occasion": obj.occasion,
            "target_audience": obj.target_audience,
            "commercial_description": obj.commercial_description,
            "proposal_id": obj.proposal_id,
            "version": obj.version,
            "parent_version": obj.parent_version,
            "refined": obj.refined,
            "refinements": list(obj.refinements),
            "score_card": serialize(obj.score_card),
            "generation_mode": obj.generation_mode,
        }
    if isinstance(obj, CommercialIntent):
        return {
            "raw_text": obj.raw_text,
            "occasion": obj.occasion,
            "quantity": obj.quantity,
            "budget_total": obj.budget_total,
            "budget_per_unit": obj.budget_per_unit,
            "target_audience": obj.target_audience,
            "preferred_categories": list(obj.preferred_categories),
            "preferred_materials": list(obj.preferred_materials),
            "preferred_colors": list(obj.preferred_colors),
            "eco": obj.eco,
            "personalizable": obj.personalizable,
            "packaging_required": obj.packaging_required,
            "generation_mode": obj.generation_mode,
            "industry": obj.industry,
            "commercial_context_tags": list(obj.commercial_context_tags),
            "segment_tags": list(obj.segment_tags),
        }
    if isinstance(obj, BudgetPlan):
        return {
            "total_budget": obj.total_budget,
            "spendable_budget": obj.spendable_budget,
            "per_unit_ceiling": obj.per_unit_ceiling,
            "margin_reserve": obj.margin_reserve,
            "quantity": obj.quantity,
            "eco_requested": obj.eco_requested,
            "utilization_target": list(obj.utilization_target),
        }
    if isinstance(obj, ProposalSetStatistics):
        return obj.to_dict()
    if isinstance(obj, ProposalSet):
        return {
            "intent": serialize(obj.intent),
            "budget_plan": serialize(obj.budget_plan),
            "proposal_count": obj.proposal_count,
            "generation_strategy": obj.generation_strategy,
            "global_observations": list(obj.global_observations),
            "reused_products": list(obj.reused_products),
            "statistics": serialize(obj.statistics),
            "proposals": [serialize(p) for p in obj.proposals],
        }
    if is_dataclass(obj):
        result = {}
        for f in fields(obj):
            value = getattr(obj, f.name)
            result[f.name] = serialize(value)
        return result
    if isinstance(obj, (list, tuple)):
        return [serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, float):
        return round(obj, 10)
    return obj


def scenario(name, query):
    return {"filename": name, "query": query}


def main():
    scenarios = [
        scenario(
            "evaluation_01_software.json",
            "Necesito 500 regalos para una empresa de software. "
            "Quiero transmitir innovación. Presupuesto máximo de 60.000 COP por unidad.",
        ),
        scenario(
            "evaluation_02_arquitectura.json",
            "Necesito 800 regalos para una firma internacional de arquitectura. "
            "Quiero transmitir innovación, elegancia y sostenibilidad. "
            "Todos deben ser personalizables. "
            "Prefiero bambú, madera o RPET. "
            "No quiero plástico de un solo uso. "
            "Presupuesto máximo de 95.000 COP por unidad.",
        ),
        scenario(
            "evaluation_03_clinica.json",
            "Necesito 400 regalos para una clínica. "
            "Quiero transmitir bienestar y confianza. "
            "Presupuesto máximo de 45.000 COP por unidad.",
        ),
        scenario(
            "evaluation_04_eco.json",
            "Necesito 1.500 regalos para una campaña ambiental. "
            "Todos deben ser ecológicos. Personalizables. "
            "Presupuesto máximo de 30.000 COP por unidad.",
        ),
        scenario(
            "evaluation_05_vip.json",
            "Necesito 200 regalos para clientes VIP. "
            "Quiero transmitir exclusividad. "
            "Presupuesto máximo de 180.000 COP por unidad.",
        ),
        scenario(
            "evaluation_06_presupuesto.json",
            "Necesito 3.800 regalos de cumpleaños. "
            "Presupuesto máximo de 25.000 COP por unidad.",
        ),
    ]

    output_dir = Path(__file__).resolve().parent
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Construyendo caso de uso...", flush=True)
    use_case = build_generate_proposal_use_case()

    total_proposals = 0
    errors = []
    all_warnings = []
    start = time.time()

    for s in scenarios:
        fname = s["filename"]
        print(f"\n--- {fname} ---", flush=True)
        print(f"Query: {s['query'][:80]}...", flush=True)
        try:
            result = use_case.execute(s["query"])
            data = serialize(result)
            path = output_dir / fname
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            n = len(result.proposals)
            total_proposals += n
            print(f"  OK -> {path} ({n} propuestas)", flush=True)
            if result.statistics:
                all_warnings.extend(result.statistics.warnings)
            for p in result.proposals:
                all_warnings.extend(p.warnings)
        except Exception as e:
            import traceback
            traceback.print_exc()
            errors.append(f"{fname}: {e}")
            print(f"  ERROR: {e}", flush=True)

    elapsed = time.time() - start

    print()
    print("=" * 56)
    print(f"  Ubicacion:          {output_dir}")
    print(f"  Tiempo total:       {elapsed:.1f}s")
    print(f"  Errores:            {len(errors)}")
    if errors:
        for e in errors:
            print(f"    - {e}")
    print(f"  Warnings:           {len(all_warnings)}")
    for w in all_warnings[:5]:
        print(f"    ! {w}")
    if len(all_warnings) > 5:
        print(f"    ... y {len(all_warnings) - 5} mas")
    print(f"  Propuestas totales: {total_proposals}")
    print("=" * 56)


if __name__ == "__main__":
    main()
