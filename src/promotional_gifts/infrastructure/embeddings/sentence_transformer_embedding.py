from typing import List

from sentence_transformers import SentenceTransformer

from ...domain.ports.embedding_port import EmbeddingPort


class SentenceTransformerEmbedding(EmbeddingPort):
    def __init__(self, model_name: str) -> None:
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, convert_to_numpy=True).tolist()
