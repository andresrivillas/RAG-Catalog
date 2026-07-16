from pathlib import Path
from typing import Dict, List

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    catalog_path: Path = BASE_DIR / "data" / "catalog" / "catalog.xlsx"
    chroma_dir: Path = BASE_DIR / "data" / "vector_stores" / "chroma"
    embedding_model: str = "all-MiniLM-L6-v2"
    collection_name: str = "promotional_gifts"
    top_k: int = 5

    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_temperature: float = 0.3
    top_p: float = 0.9
    max_tokens: int = 400
    prompts_path: Path = BASE_DIR / "prompts"
    enriched_path: Path = BASE_DIR / "data" / "enriched" / "enriched_catalog.json"
    proposals_dir: Path = BASE_DIR / "data" / "proposals"
    negative_categories: List[str] = [
        "medico", "medicina", "insumo medico", "hospitalario",
        "industrial", "industria", "materia prima", "produccion",
        "quimico", "limpieza industrial", "maquinaria",
    ]
    evaluation_weights: Dict[str, float] = {
        "budget": 0.20,
        "commercial": 0.25,
        "diversity": 0.10,
        "category_diversity": 0.08,
        "coherence": 0.15,
        "utility": 0.07,
        "brand": 0.05,
        "premium": 0.05,
        "eco": 0.05,
        "personalization": 0.05,
        "occasion": 0.15,
        "audience": 0.10,
        "balance": 0.05,
    }
    evaluation_debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
