from dataclasses import dataclass


@dataclass
class RankingScore:
    semantic_score: float = 0.0
    material_score: float = 0.0
    category_score: float = 0.0
    price_score: float = 0.0
    quality_score: float = 0.0
    eco_score: float = 0.0
    audience_score: float = 0.0
    attribute_score: float = 0.0
    final_score: float = 0.0
    ranking_reason: str = ""
