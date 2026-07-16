from typing import List

from ...domain.entities.commercial_proposal import CommercialProposal
from ...domain.entities.proposal_set import ProposalSet
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

    def write_set(
        self,
        proposal_set: ProposalSet,
        model: str,
        temperature: float,
    ) -> None:
        """Unica llamada al LLM con todo el set en contexto. Distribuye las
        secciones redactadas a cada propuesta por indice.
        """
        if not proposal_set.proposals:
            return
        context = self.context_builder.build_set(proposal_set)
        template = self.prompt_loader.load(self.proposal_prompt)
        system_rules = self.prompt_loader.load(self.system_prompt)

        final_prompt = f"{system_rules}\n\n{template.replace('{context}', context)}"
        raw = self.llm.generate(
            prompt=final_prompt, temperature=temperature, model=model
        )

        sections = self._parse_sections(raw)
        for index, proposal in enumerate(proposal_set.proposals, start=1):
            proposal.commercial_description = sections.get(index, "").strip()

    def _parse_sections(self, raw: str) -> dict:
        sections: dict = {}
        current: int = None
        buffer: List[str] = []
        for line in raw.splitlines():
            marker = None
            stripped = line.strip()
            if stripped.startswith("===PROPUESTA "):
                try:
                    marker = int(stripped.split("===PROPUESTA")[1].split("===")[0].strip())
                except (ValueError, IndexError):
                    marker = None
            if marker is not None:
                if current is not None:
                    sections[current] = "\n".join(buffer).strip()
                current = marker
                buffer = []
            elif current is not None:
                buffer.append(line)
        if current is not None:
            sections[current] = "\n".join(buffer).strip()
        return sections
