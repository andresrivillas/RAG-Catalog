from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ..entities.commercial_proposal import CommercialProposal, ProposalItem
from ..entities.commercial_intent import CommercialIntent
from ..services.budget_plan import BudgetPlan


@dataclass
class ProposalComparison:
    proposal_a_index: int
    proposal_b_index: int
    shared_reference_count: int
    shared_reference_ratio: float
    shared_category_ratio: float
    role_overlap_ratio: float
    material_overlap_ratio: float
    perceived_value_overlap_ratio: float
    strategy_overlap: bool
    similarity: float

    def to_dict(self) -> dict:
        return {
            "proposal_a_index": self.proposal_a_index,
            "proposal_b_index": self.proposal_b_index,
            "shared_reference_count": self.shared_reference_count,
            "shared_reference_ratio": round(self.shared_reference_ratio, 3),
            "shared_category_ratio": round(self.shared_category_ratio, 3),
            "role_overlap_ratio": round(self.role_overlap_ratio, 3),
            "material_overlap_ratio": round(self.material_overlap_ratio, 3),
            "perceived_value_overlap_ratio": round(self.perceived_value_overlap_ratio, 3),
            "strategy_overlap": self.strategy_overlap,
            "similarity": round(self.similarity, 3),
        }


class DiversityEngine:
    """Evalua la diversidad entre propuestas de un mismo ProposalSet y decide
    si es necesario reconstruir la propuesta peor posicionada cuando dos
    propuestas son demasiado similares.

    La similitud combina: solapamiento de productos (referencias), de
    categorias, de roles, de materiales y de nivel de valor percibido, asi
    como si comparten la misma estrategia/comercial. Un umbral configurable
    (`similarity_threshold`) define cuando una reconstruccion es obligatoria.
    """

    def __init__(self, similarity_threshold: float = 0.6) -> None:
        self.similarity_threshold = similarity_threshold

    # ----- extractores de caracteristicas -----

    def _references(self, proposal: CommercialProposal) -> set:
        return {it.reference for it in proposal.items if it.reference}

    def _categories(self, proposal: CommercialProposal) -> set:
        return {
            (it.category or "").strip().lower()
            for it in proposal.items
            if it.category
        }

    def _roles(self, proposal: CommercialProposal) -> set:
        return {
            (it.role or "").strip().upper()
            for it in proposal.items
            if it.role
        }

    def _materials(self, proposal: CommercialProposal) -> set:
        mats: set = set()
        for it in proposal.items:
            for tok in (it.materials or "").lower().replace(";", " ").replace(",", " ").split():
                if tok:
                    mats.add(tok)
        return mats

    def _perceived_values(self, proposal: CommercialProposal) -> set:
        return {
            (it.perceived_value_level or "medio").strip().lower()
            for it in proposal.items
        }

    def _strategy_key(self, proposal: CommercialProposal) -> str:
        return (proposal.generation_mode or "balanced").strip().lower()

    # ----- similitud entre un par -----

    def compare(
        self, a: CommercialProposal, b: CommercialProposal
    ) -> float:
        refs_a, refs_b = self._references(a), self._references(b)
        cats_a, cats_b = self._categories(a), self._categories(b)
        roles_a, roles_b = self._roles(a), self._roles(b)
        mats_a, mats_b = self._materials(a), self._materials(b)
        vals_a, vals_b = self._perceived_values(a), self._perceived_values(b)

        # Solapamiento productos (Jaccard de referencias).
        shared_refs = refs_a & refs_b
        ref_ratio = _jaccard(refs_a, refs_b)
        # Solapamiento categorias.
        cat_ratio = _jaccard(cats_a, cats_b)
        # Solapamiento roles.
        role_ratio = _jaccard(roles_a, roles_b)
        # Solapamiento materiales.
        mat_ratio = _jaccard(mats_a, mats_b)
        # Solapamiento valor percibido.
        val_ratio = _jaccard(vals_a, vals_b)
        # Estrategia comun (0/1).
        strategy_overlap = self._strategy_key(a) == self._strategy_key(b)

        # Pesos: productos y categorias son los senaladores mas fuertes.
        similarity = (
            ref_ratio * 0.42
            + cat_ratio * 0.22
            + role_ratio * 0.14
            + mat_ratio * 0.12
            + val_ratio * 0.10
        )
        if strategy_overlap:
            # Misma estrategia/comercial suma una penalizacion extra: empuja
            # hacia arriba la similitud para forzar reconstruccion.
            similarity = max(similarity, similarity + 0.12)
            similarity = min(similarity, 1.0)

        # Guardamos metadatos utiles en un objeto comparado.
        comparison = ProposalComparison(
            proposal_a_index=-1,
            proposal_b_index=-1,
            shared_reference_count=len(shared_refs),
            shared_reference_ratio=ref_ratio,
            shared_category_ratio=cat_ratio,
            role_overlap_ratio=role_ratio,
            material_overlap_ratio=mat_ratio,
            perceived_value_overlap_ratio=val_ratio,
            strategy_overlap=strategy_overlap,
            similarity=similarity,
        )
        return similarity

    # ----- similitud global sobre el set -----

    def max_similarity(self, proposals: List[CommercialProposal]) -> float:
        if len(proposals) < 2:
            return 0.0
        worst = 0.0
        for i in range(len(proposals)):
            for j in range(i + 1, len(proposals)):
                s = self.compare(proposals[i], proposals[j])
                if s > worst:
                    worst = s
        return worst

    def needs_rebuild(
        self,
        proposals: List[CommercialProposal],
        scores: Optional[List[float]] = None,
    ) -> Optional[Tuple[int, int, float]]:
        """Devuelve (indice_peor, indice_mejor, similitud) si la propuesta peor
        posicionada es demasiado similar a otra; si no, None.
        """
        if len(proposals) < 2:
            return None
        scores = scores if scores is not None else [p.score for p in proposals]
        # Par mas similar global.
        best_pair = None
        best_sim = 0.0
        for i in range(len(proposals)):
            for j in range(i + 1, len(proposals)):
                s = self.compare(proposals[i], proposals[j])
                if s > best_sim:
                    best_sim = s
                    best_pair = (i, j)
        if best_pair is None or best_sim < self.similarity_threshold:
            return None
        i, j = best_pair
        # La peor es la de menor score del par.
        if scores[i] <= scores[j]:
            return (i, j, best_sim)
        return (j, i, best_sim)

    # ----- reconstruccion dirigida -----

    def blacklist_from(self, proposals: List[CommercialProposal], exclude_index: int) -> set:
        """Productos a penalizar en la reconstruccion de la propuesta en
        `exclude_index`: todos los productos de las OTRAS propuestas (blacklist
        dinamica). No se eliminan, solo se baja prioridad.
        """
        refs: set = set()
        for idx, p in enumerate(proposals):
            if idx == exclude_index:
                continue
            refs |= self._references(p)
        return refs


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    inter = a & b
    return len(inter) / len(union)
