from typing import List

from ...domain.entities.commercial_proposal import CommercialProposal
from ...domain.ports.llm_port import LLMPort
from .prompt_context_builder import PromptContextBuilder
from .prompt_loader import PromptLoader


class CommercialWriter:
    def __init__(
        self,
        llm: LLMPort,
        prompt_loader: PromptLoader,
        context_builder: PromptContextBuilder,
        system_prompt: str = "system/global_rules.txt",
        proposal_prompt: str = "commercial/proposal_writer.txt",
    ) -> None:
        self.llm = llm
        self.prompt_loader = prompt_loader
        self.context_builder = context_builder
        self.system_prompt = system_prompt
        self.proposal_prompt = proposal_prompt

    def write(
        self,
        proposal: CommercialProposal,
        model: str,
        temperature: float,
        refinement_context: str = None,
    ) -> str:
        if refinement_context is not None:
            context = refinement_context
        else:
            context = self.context_builder.build(proposal)
        template = self.prompt_loader.load(self.proposal_prompt)
        system_rules = self.prompt_loader.load(self.system_prompt)

        final_prompt = f"{system_rules}\n\n{template.replace('{context}', context)}"
        return self.llm.generate(
            prompt=final_prompt, temperature=temperature, model=model
        )
