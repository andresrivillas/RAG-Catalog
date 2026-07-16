from pathlib import Path
from typing import List


class PromptLoader:
    def __init__(self, prompts_path: Path) -> None:
        self.prompts_path = Path(prompts_path)

    def load(self, relative_path: str) -> str:
        file_path = self.prompts_path / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt no encontrado: {file_path}")
        return file_path.read_text(encoding="utf-8")

    def load_many(self, relative_paths: List[str]) -> str:
        return "\n\n".join(self.load(p) for p in relative_paths)
