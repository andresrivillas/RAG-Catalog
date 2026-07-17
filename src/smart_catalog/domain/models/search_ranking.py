from dataclasses import dataclass, field


@dataclass
class SearchRanking:
    embedding_score: float = 0.0
    keyword_score: float = 0.0
    popularity_score: float = 0.0
    combined_score: float = 0.0
    weights: dict[str, float] = field(default_factory=lambda: {
        "embedding": 0.5,
        "keyword": 0.3,
        "popularity": 0.2,
    })
