from pathlib import Path
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

    class Config:
        env_file = ".env"


settings = Settings()
