from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    catalog_path: Path = BASE_DIR / "data" / "catalog" / "catalog.xlsx"
    chroma_dir: Path = BASE_DIR / "data" / "vector_stores" / "chroma"
    embedding_model: str = "all-MiniLM-L6-v2"
    collection_name: str = "promotional_gifts"
    top_k: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
