import datetime
import uuid

from ..context import ProposalContext


class PersistenceStage:
    def execute(self, ctx: ProposalContext) -> None:
        if ctx.workspace is None or ctx.proposal_set is None:
            return
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        root = f"prop-{stamp}-{uuid.uuid4().hex[:4]}"
        for index, proposal in enumerate(ctx.proposal_set.proposals, start=1):
            if not proposal.proposal_id:
                proposal.proposal_id = f"{root}__v{index}"
            ctx.workspace.create_document(
                proposal=proposal,
                intent=ctx.intent,
                original_query=ctx.text,
                score_card=proposal.score_card,
                client="",
            )
