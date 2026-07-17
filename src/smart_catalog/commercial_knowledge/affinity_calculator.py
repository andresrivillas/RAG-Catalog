import logging
import re
from typing import Optional

from ..domain.models.structured_search_query import StructuredSearchQuery
from ..domain.models.search_intent import SearchIntent
from .models import CommercialKnowledge, AUDIENCE_TO_INDUSTRY, INDUSTRY_SYNONYMS, PROFILE_SYNONYMS

logger = logging.getLogger("smart_catalog.commercial_affinity")


class CommercialAffinityCalculator:

    def calculate(
        self,
        query: StructuredSearchQuery,
        intent: Optional[SearchIntent],
        knowledge: CommercialKnowledge,
    ) -> tuple[float, list[str], dict[str, float]]:
        score = 0.0
        reasons: list[str] = []
        factors: dict[str, float] = {}

        if knowledge.confidence < 0.2:
            return 0.0, ["Conocimiento comercial insuficiente"], {"base": 0.0}

        q_text = query.original_query.lower()

        aud = self._compute_audience_factor(query, intent, knowledge)
        if aud["score"] > 0:
            score += aud["score"]
            factors["audiencia_industria"] = aud["score"]
            if aud["reason"]:
                reasons.append(aud["reason"])

        con = self._compute_concept_factor(query, intent, knowledge)
        if con["score"] > 0:
            score += con["score"]
            factors["concepto"] = con["score"]
            if con["reason"]:
                reasons.append(con["reason"])

        pro = self._compute_profile_factor(query, intent, knowledge, q_text)
        if pro["score"] > 0:
            score += pro["score"]
            factors["perfil_cliente"] = pro["score"]
            if pro["reason"]:
                reasons.append(pro["reason"])

        occ = self._compute_occasion_factor(query, intent, knowledge, q_text)
        if occ["score"] > 0:
            score += occ["score"]
            factors["ocasion_uso"] = occ["score"]
            if occ["reason"]:
                reasons.append(occ["reason"])

        cor = self._compute_corporate_factor(query, intent, knowledge, q_text)
        if cor["score"] > 0:
            score += cor["score"]
            factors["afinidad_corporativa"] = cor["score"]
            if cor["reason"]:
                reasons.append(cor["reason"])

        pre = self._compute_prestige_factor(query, intent, knowledge)
        if pre["score"] > 0:
            score += pre["score"]
            factors["prestigio"] = pre["score"]
            if pre["reason"]:
                reasons.append(pre["reason"])

        score = min(score, 1.0)
        return round(score, 4), reasons, factors

    def _compute_audience_factor(
        self,
        query: StructuredSearchQuery,
        intent: Optional[SearchIntent],
        knowledge: CommercialKnowledge,
    ) -> dict:
        audience = None
        if intent and intent.detected_audience:
            audience = intent.detected_audience

        if not audience:
            for pattern, industry in AUDIENCE_TO_INDUSTRY.items():
                pat_lower = pattern.lower().replace("_", " ")
                if pat_lower in query.original_query.lower():
                    audience = pattern
                    break

        if audience:
            industry = AUDIENCE_TO_INDUSTRY.get(audience, "")
            if industry and industry in knowledge.industry_affinity:
                return {
                    "score": 0.25,
                    "reason": f"Se recomienda para el sector {industry.lower()}",
                }
            for ind, synonyms in INDUSTRY_SYNONYMS.items():
                if audience.lower() in [s.lower() for s in synonyms]:
                    if ind in knowledge.industry_affinity:
                        return {
                            "score": 0.2,
                            "reason": f"Afinidad con industria {ind.lower()}",
                        }
        return {"score": 0.0, "reason": ""}

    def _compute_concept_factor(
        self,
        query: StructuredSearchQuery,
        intent: Optional[SearchIntent],
        knowledge: CommercialKnowledge,
    ) -> dict:
        q = query.original_query.lower()
        score = 0.0
        reasons = []

        is_premium_query = (
            query.detected_quality_intent == "HIGH_QUALITY"
            or query.detected_price_intent == "HIGH_PRICE"
            or any(w in q for w in ["premium", "lujo", "lujoso", "alta gama", "exclusivo", "elegante"])
        )
        if is_premium_query:
            if knowledge.premium_level in ("premium", "luxury"):
                score = max(score, 0.2)
                reasons.append("Pertenece al segmento premium")

        is_eco_query = query.detected_eco_intent or any(
            w in q for w in ["ecologico", "sostenible", "eco", "verde", "reciclado"]
        )
        if is_eco_query:
            if "ecologico" in knowledge.commercial_tags or "sostenible" in knowledge.commercial_tags:
                score = max(score, 0.18)
                reasons.append("Es un producto ecologico y sostenible")

        is_economic_query = (
            query.detected_price_intent == "LOW_PRICE"
            or any(w in q for w in ["barato", "economico", "accesible", "bajo costo"])
        )
        if is_economic_query:
            if knowledge.commercial_value == "economic":
                score = max(score, 0.15)
                reasons.append("Es una opcion economica")

        is_executive_query = any(
            w in q for w in ["ejecutivo", "ejecutiva", "profesional", "corporativo"]
        )
        if is_executive_query:
            if knowledge.executive_level in ("high", "medium"):
                score = max(score, 0.15)
                reasons.append("Adecuado para perfil ejecutivo")
            if "corporativo" in knowledge.commercial_tags:
                score = max(score, 0.18)
                reasons.append("Producto de uso corporativo")

        is_tech_query = any(
            w in q for w in ["tecnologico", "tecnologia", "tech", "digital", "innovacion"]
        )
        if is_tech_query:
            if "tecnologico" in knowledge.commercial_tags:
                score = max(score, 0.18)
                reasons.append("Producto tecnologico")
            if "TECNOLOGIA" in knowledge.industry_affinity:
                score = max(score, 0.2)
                reasons.append("Recomendado para el sector tecnologico")

        if reasons:
            return {"score": min(score, 0.25), "reason": reasons[0]}
        return {"score": 0.0, "reason": ""}

    def _compute_profile_factor(
        self,
        query: StructuredSearchQuery,
        intent: Optional[SearchIntent],
        knowledge: CommercialKnowledge,
        q_text: str,
    ) -> dict:
        score = 0.0
        reasons = []

        for profile, synonyms in PROFILE_SYNONYMS.items():
            for syn in synonyms:
                if syn in q_text:
                    if profile in knowledge.customer_profiles:
                        score = max(score, 0.18)
                        reasons.append(
                            f"Se recomienda para perfiles {profile.lower()}"
                        )
                    elif profile == "VIP" and knowledge.executive_level == "high":
                        score = max(score, 0.15)
                        reasons.append("Adecuado para clientes VIP")
                    break

        is_vip = any(w in q_text for w in ["vip", "cliente especial", "cliente premium", "exclusivo"])
        if is_vip:
            if knowledge.executive_level == "high" or knowledge.premium_level in ("premium", "luxury"):
                score = max(score, 0.2)
                reasons.append("Recomendado para clientes VIP")

        is_cliente = any(w in q_text for w in ["clientes", "cliente"])
        if is_cliente and not is_vip:
            if knowledge.corporate_affinity > 0.6:
                score = max(score, 0.12)
                reasons.append("Adecuado como regalo para clientes")

        if reasons:
            return {"score": min(score, 0.2), "reason": reasons[0]}
        return {"score": 0.0, "reason": ""}

    def _compute_occasion_factor(
        self,
        query: StructuredSearchQuery,
        intent: Optional[SearchIntent],
        knowledge: CommercialKnowledge,
        q_text: str,
    ) -> dict:
        occasion_map = {
            "evento": "EVENTOS",
            "feria": "FERIAS",
            "bienvenida": "BIENVENIDA",
            "capacitacion": "CAPACITACION",
            "conferencia": "CONFERENCIAS",
            "congreso": "CONGRESOS",
            "convencion": "CONVENCION",
            "lanzamiento": "LANZAMIENTOS",
            "reconocimiento": "RECONOCIMIENTO",
            "premio": "PREMIOS",
            "viaje": "VIAJES",
            "workshop": "WORKSHOP",
            "reunion": "REUNIONES",
            "corporativo": "EVENTO_CORPORATIVO",
            "inauguracion": "LANZAMIENTOS",
        }

        for kw, occasion in occasion_map.items():
            if kw in q_text:
                gift_upper = [o.upper() for o in knowledge.gift_occasions]
                use_upper = [u.upper() for u in knowledge.use_cases]

                if occasion in gift_upper or occasion in use_upper:
                    return {
                        "score": 0.15,
                        "reason": f"Regalo frecuente en {kw}s",
                    }

        for occasion in knowledge.gift_occasions:
            occ_lower = occasion.lower().replace("_", " ")
            if occ_lower in q_text:
                return {
                    "score": 0.15,
                    "reason": f"Recomendado para {occ_lower}",
                }

        return {"score": 0.0, "reason": ""}

    def _compute_corporate_factor(
        self,
        query: StructuredSearchQuery,
        intent: Optional[SearchIntent],
        knowledge: CommercialKnowledge,
        q_text: str,
    ) -> dict:
        is_corporate = any(
            w in q_text for w in ["corporativo", "empresa", "empresarial", "organizacion", "comercial"]
        )
        if is_corporate:
            if knowledge.corporate_affinity > 0.6:
                return {
                    "score": 0.15,
                    "reason": "Alta afinidad corporativa",
                }
        return {"score": 0.0, "reason": ""}

    def _compute_prestige_factor(
        self,
        query: StructuredSearchQuery,
        intent: Optional[SearchIntent],
        knowledge: CommercialKnowledge,
    ) -> dict:
        score = 0.0
        reasons = []

        if knowledge.premium_level in ("premium", "luxury"):
            score += 0.08
            reasons.append("Pertenece al segmento premium")
        if knowledge.executive_level == "high":
            score += 0.06
            reasons.append("Producto de nivel ejecutivo")
        if knowledge.corporate_affinity > 0.7:
            score += 0.06
            reasons.append("Alta percepcion corporativa")

        if reasons:
            return {"score": min(score, 0.15), "reason": reasons[0]}
        return {"score": 0.0, "reason": ""}

    def compute_blend_alpha(self, query: StructuredSearchQuery) -> float:
        q = query.original_query.lower()
        if query.detected_audience:
            return 0.45
        if query.detected_quality_intent or query.detected_price_intent:
            return 0.35
        if query.detected_eco_intent:
            return 0.3
        if any(w in q for w in ["vip", "ejecutivo", "corporativo", "premium", "elegante",
                                 "moderno", "util", "economico", "sostenible"]):
            return 0.35
        if any(w in q for w in ["regalo", "cliente", "evento", "feria"]):
            return 0.4
        return 0.1
