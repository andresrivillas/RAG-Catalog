import datetime
from typing import Any, Dict, List

from ...entities.commercial_intent import CommercialIntent
from ...entities.commercial_proposal import CommercialProposal, ProposalItem
from ...entities.proposal_document import (
    ProposalDocument,
    RefinementRecord,
)
from ...services.decision_trace import DecisionTrace
from ...services.evaluation.proposal_score_card import (
    CriterionResult,
    ProposalScoreCard,
)
from ...value_objects.money import Money


def _now() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def money_to_dict(m: Money) -> dict:
    return {"amount": m.amount, "currency": m.currency}


def dict_to_money(d: dict) -> Money:
    return Money(amount=float(d.get("amount", 0.0)), currency=d.get("currency", "COP"))


def decision_trace_to_dict(t: DecisionTrace) -> dict:
    return {
        "semantic_score": t.semantic_score,
        "commercial_score": t.commercial_score,
        "occasion_score": t.occasion_score,
        "budget_score": t.budget_score,
        "final_score": t.final_score,
        "reason": t.reason,
        "detail": t.detail,
    }


def dict_to_decision_trace(d: dict) -> DecisionTrace:
    return DecisionTrace(
        semantic_score=float(d.get("semantic_score", 0.0)),
        commercial_score=float(d.get("commercial_score", 0.0)),
        occasion_score=float(d.get("occasion_score", 0.0)),
        budget_score=float(d.get("budget_score", 0.0)),
        final_score=float(d.get("final_score", 0.0)),
        reason=d.get("reason", ""),
        detail=d.get("detail", {}),
    )


def item_to_dict(item: ProposalItem) -> dict:
    return {
        "reference": item.reference,
        "name": item.name,
        "unit_price": money_to_dict(item.unit_price),
        "quantity": item.quantity,
        "role": item.role,
        "selection_reason": item.selection_reason,
        "decision_trace": decision_trace_to_dict(item.decision_trace)
        if item.decision_trace
        else None,
        "thumbnail_url": item.thumbnail_url,
        "detail_url": item.detail_url,
        "category": item.category,
        "materials": item.materials,
        "colors": item.colors,
        "capacity": item.capacity,
        "customization": item.customization,
        "eco": item.eco,
        "personalizable": item.personalizable,
        "perceived_value_level": item.perceived_value_level,
    }


def dict_to_item(d: dict) -> ProposalItem:
    return ProposalItem(
        reference=d.get("reference", ""),
        name=d.get("name", ""),
        unit_price=dict_to_money(d.get("unit_price", {})),
        quantity=int(d.get("quantity", 0)),
        role=d.get("role", ""),
        selection_reason=d.get("selection_reason", ""),
        decision_trace=dict_to_decision_trace(d["decision_trace"])
        if d.get("decision_trace")
        else None,
        thumbnail_url=d.get("thumbnail_url", ""),
        detail_url=d.get("detail_url", ""),
        category=d.get("category", ""),
        materials=d.get("materials", ""),
        colors=d.get("colors", ""),
        capacity=d.get("capacity", ""),
        customization=d.get("customization", ""),
        eco=d.get("eco", False),
        personalizable=d.get("personalizable", False),
        perceived_value_level=d.get("perceived_value_level", ""),
    )


def intent_to_dict(intent: CommercialIntent) -> dict:
    return {
        "raw_text": intent.raw_text,
        "occasion": intent.occasion,
        "quantity": intent.quantity,
        "budget_total": intent.budget_total,
        "budget_per_unit": intent.budget_per_unit,
        "target_audience": intent.target_audience,
        "preferred_categories": list(intent.preferred_categories),
        "preferred_materials": list(intent.preferred_materials),
        "preferred_colors": list(intent.preferred_colors),
        "eco": intent.eco,
        "personalizable": intent.personalizable,
        "packaging_required": intent.packaging_required,
        "generation_mode": intent.generation_mode,
    }


def dict_to_intent(d: dict) -> CommercialIntent:
    return CommercialIntent(
        raw_text=d.get("raw_text", ""),
        occasion=d.get("occasion"),
        quantity=d.get("quantity"),
        budget_total=d.get("budget_total"),
        budget_per_unit=d.get("budget_per_unit"),
        target_audience=d.get("target_audience"),
        preferred_categories=list(d.get("preferred_categories", [])),
        preferred_materials=list(d.get("preferred_materials", [])),
        preferred_colors=list(d.get("preferred_colors", [])),
        eco=bool(d.get("eco", False)),
        personalizable=bool(d.get("personalizable", False)),
        packaging_required=bool(d.get("packaging_required", False)),
        generation_mode=d.get("generation_mode", "balanced"),
    )


def score_card_to_dict(card: ProposalScoreCard) -> dict:
    return {
        "overall_score": card.overall_score,
        "budget_score": card.budget_score,
        "commercial_score": card.commercial_score,
        "coherence_score": card.coherence_score,
        "diversity_score": card.diversity_score,
        "category_diversity_score": card.category_diversity_score,
        "utility_score": card.utility_score,
        "brand_visibility_score": card.brand_visibility_score,
        "premium_score": card.premium_score,
        "eco_score": card.eco_score,
        "personalization_score": card.personalization_score,
        "occasion_score": card.occasion_score,
        "audience_score": card.audience_score,
        "balance_score": card.balance_score,
        "criteria": [c.to_dict() for c in card.criteria],
        "observations": list(card.observations),
    }


def dict_to_score_card(d: dict) -> ProposalScoreCard:
    if not d:
        return None
    return ProposalScoreCard(
        overall_score=float(d.get("overall_score", 0.0)),
        budget_score=float(d.get("budget_score", 0.0)),
        commercial_score=float(d.get("commercial_score", 0.0)),
        coherence_score=float(d.get("coherence_score", 0.0)),
        diversity_score=float(d.get("diversity_score", 0.0)),
        category_diversity_score=float(d.get("category_diversity_score", 0.0)),
        utility_score=float(d.get("utility_score", 0.0)),
        brand_visibility_score=float(d.get("brand_visibility_score", 0.0)),
        premium_score=float(d.get("premium_score", 0.0)),
        eco_score=float(d.get("eco_score", 0.0)),
        personalization_score=float(d.get("personalization_score", 0.0)),
        occasion_score=float(d.get("occasion_score", 0.0)),
        audience_score=float(d.get("audience_score", 0.0)),
        balance_score=float(d.get("balance_score", 0.0)),
        criteria=[CriterionResult(**c) for c in d.get("criteria", [])],
        observations=list(d.get("observations", [])),
    )


def proposal_to_dict(p: CommercialProposal) -> dict:
    return {
        "name": p.name,
        "score": p.score,
        "items": [item_to_dict(i) for i in p.items],
        "total_cost": money_to_dict(p.total_cost),
        "per_unit_cost": money_to_dict(p.per_unit_cost),
        "warnings": list(p.warnings),
        "occasion": p.occasion,
        "target_audience": p.target_audience,
        "commercial_description": p.commercial_description,
        "proposal_id": p.proposal_id,
        "version": p.version,
        "parent_version": p.parent_version,
        "refined": p.refined,
        "refinements": list(p.refinements),
        "score_card": score_card_to_dict(p.score_card) if p.score_card else None,
    }


def dict_to_proposal(d: dict) -> CommercialProposal:
    p = CommercialProposal(
        name=d.get("name", ""),
        score=float(d.get("score", 0.0)),
        items=[dict_to_item(i) for i in d.get("items", [])],
        total_cost=dict_to_money(d.get("total_cost", {})),
        per_unit_cost=dict_to_money(d.get("per_unit_cost", {})),
        warnings=list(d.get("warnings", [])),
        occasion=d.get("occasion", ""),
        target_audience=d.get("target_audience", ""),
        commercial_description=d.get("commercial_description", ""),
        proposal_id=d.get("proposal_id", ""),
        version=int(d.get("version", 1)),
        parent_version=int(d.get("parent_version", 0)),
        refined=bool(d.get("refined", False)),
        refinements=list(d.get("refinements", [])),
    )
    p.score_card = dict_to_score_card(d.get("score_card"))
    return p


def document_to_dict(doc: ProposalDocument) -> dict:
    return {
        "proposal_id": doc.proposal_id,
        "version": doc.version,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at,
        "original_query": doc.original_query,
        "client": doc.client,
        "intent": intent_to_dict(doc.intent),
        "proposal": proposal_to_dict(doc.proposal),
        "score_card": score_card_to_dict(doc.score_card) if doc.score_card else None,
        "refinement_history": [r.to_dict() for r in doc.refinement_history],
    }


def dict_to_document(d: dict) -> ProposalDocument:
    return ProposalDocument(
        proposal_id=d.get("proposal_id", ""),
        version=int(d.get("version", 1)),
        created_at=d.get("created_at", _now()),
        updated_at=d.get("updated_at", _now()),
        original_query=d.get("original_query", ""),
        client=d.get("client", ""),
        intent=dict_to_intent(d.get("intent", {})),
        proposal=dict_to_proposal(d.get("proposal", {})),
        score_card=dict_to_score_card(d.get("score_card")) or None,
        refinement_history=[
            RefinementRecord.from_dict(r) for r in d.get("refinement_history", [])
        ],
    )
