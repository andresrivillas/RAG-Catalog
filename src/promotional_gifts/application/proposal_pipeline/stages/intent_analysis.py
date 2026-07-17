from typing import Optional

from ....domain.entities.commercial_intent import CommercialIntent
from ....domain.ports.intent_analyzer_port import IntentAnalyzerPort
from ..context import ProposalContext


class IntentAnalysisStage:
    def __init__(self, analyzer: IntentAnalyzerPort) -> None:
        self._analyzer = analyzer

    def execute(self, ctx: ProposalContext) -> None:
        if ctx.intent is None:
            ctx.intent = self._analyzer.analyze(ctx.text)
        if ctx.mode is not None:
            ctx.intent.generation_mode = ctx.mode.value
