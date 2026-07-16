from typing import Optional

import ollama

from ...domain.ports.llm_port import LLMPort


class OllamaLLM(LLMPort):
    def __init__(self, host: str, top_p: float, max_tokens: int) -> None:
        self.client = ollama.Client(host=host)
        self.top_p = top_p
        self.max_tokens = max_tokens

    def generate(self, prompt: str, temperature: float, model: str) -> str:
        response = self.client.generate(
            model=model,
            prompt=prompt,
            options={
                "temperature": temperature,
                "top_p": self.top_p,
                "num_predict": self.max_tokens,
            },
        )
        return response["response"].strip()
