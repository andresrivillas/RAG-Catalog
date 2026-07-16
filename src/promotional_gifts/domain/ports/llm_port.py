from abc import ABC, abstractmethod


class LLMPort(ABC):
    @abstractmethod
    def generate(self, prompt: str, temperature: float, model: str) -> str:
        raise NotImplementedError
