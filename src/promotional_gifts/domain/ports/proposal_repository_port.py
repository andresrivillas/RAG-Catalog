from typing import List, Optional

from ..entities.proposal_document import ProposalDocument


class ProposalRepositoryPort:
    def save(self, document: ProposalDocument) -> None:
        raise NotImplementedError

    def get(self, proposal_id: str) -> Optional[ProposalDocument]:
        raise NotImplementedError

    def delete(self, proposal_id: str) -> None:
        raise NotImplementedError

    def list_ids(self) -> List[str]:
        raise NotImplementedError

    def list_documents(self) -> List[ProposalDocument]:
        raise NotImplementedError
