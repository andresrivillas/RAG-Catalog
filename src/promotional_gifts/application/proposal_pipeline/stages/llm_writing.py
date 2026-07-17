from ..context import ProposalContext


class LlmWritingStage:
    def execute(self, ctx: ProposalContext) -> None:
        if ctx.commercial_writer is None or ctx.proposal_set is None:
            return
        ctx.commercial_writer.write_set(
            ctx.proposal_set,
            model=ctx.llm_model,
            temperature=ctx.llm_temperature,
        )
