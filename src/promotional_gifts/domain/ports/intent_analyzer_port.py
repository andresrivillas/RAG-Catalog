from abc import ABC, abstractmethod

from ..entities.commercial_intent import CommercialIntent


class IntentAnalyzerPort(ABC):
    @abstractmethod
    def analyze(self, text: str) -> CommercialIntent:
        raise NotImplementedError
