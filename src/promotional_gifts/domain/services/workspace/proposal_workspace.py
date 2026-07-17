import datetime
import uuid
from typing import List, Optional

from ...entities.commercial_intent import CommercialIntent
from ...entities.proposal_document import (
    ProposalDocument,
    RefinementRecord,
)
from ...entities.commercial_proposal import CommercialProposal
from ...ports.proposal_repository_port import ProposalRepositoryPort


class ProposalWorkspace:
    def __init__(self, repository: ProposalRepositoryPort) -> None:
        self.repository = repository

    def _root_id(self) -> str:
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"prop-{stamp}-{uuid.uuid4().hex[:4]}"

    def _version_from_id(self, proposal_id: str, fallback: int = 1) -> int:
        if "__v" not in proposal_id:
            return fallback
        suffix = proposal_id.rsplit("__v", 1)[-1]
        return int(suffix) if suffix.isdigit() else fallback

    def create_document(
        self,
        proposal: CommercialProposal,
        intent: CommercialIntent,
        original_query: str,
        score_card=None,
        client: str = "",
    ) -> ProposalDocument:
        proposal_id = proposal.proposal_id or self._root_id()
        version = self._version_from_id(proposal_id, proposal.version)
        proposal.proposal_id = proposal_id
        proposal.version = version
        doc = ProposalDocument(
            proposal_id=proposal_id,
            version=version,
            created_at=datetime.datetime.now().isoformat(timespec="seconds"),
            updated_at=datetime.datetime.now().isoformat(timespec="seconds"),
            original_query=original_query,
            intent=intent,
            proposal=proposal,
            score_card=score_card,
            client=client,
        )
        self.repository.save(doc)
        return doc

    def save_version(
        self,
        proposal: CommercialProposal,
        intent: CommercialIntent,
        original_query: str,
        score_card=None,
        parent_doc: Optional[ProposalDocument] = None,
        refinement: Optional[RefinementRecord] = None,
        client: str = "",
    ) -> ProposalDocument:
        if parent_doc is None:
            return self.create_document(
                proposal, intent, original_query, score_card, client
            )
        root = parent_doc.root_id
        version = parent_doc.version + 1
        doc = ProposalDocument(
            proposal_id=f"{root}__v{version}",
            version=version,
            created_at=parent_doc.created_at,
            updated_at=datetime.datetime.now().isoformat(timespec="seconds"),
            original_query=parent_doc.original_query,
            intent=intent,
            proposal=proposal,
            score_card=score_card,
            client=parent_doc.client or client,
        )
        history = list(parent_doc.refinement_history)
        if refinement is not None:
            history.append(refinement)
        doc.refinement_history = history
        self.repository.save(doc)
        return doc

    def open(self, proposal_id: str) -> Optional[ProposalDocument]:
        return self.repository.get(proposal_id)

    def update(self, document: ProposalDocument) -> None:
        self.repository.save(document)

    def delete(self, proposal_id: str) -> None:
        self.repository.delete(proposal_id)

    def duplicate(self, proposal_id: str) -> Optional[ProposalDocument]:
        doc = self.repository.get(proposal_id)
        if doc is None:
            return None
        new = self.create_document(
            proposal=doc.proposal,
            intent=doc.intent,
            original_query=doc.original_query,
            score_card=doc.score_card,
            client=doc.client,
        )
        return new

    def list_documents(self) -> List[ProposalDocument]:
        return self.repository.list_documents()

    def get_versions(self, root_id: str) -> List[ProposalDocument]:
        versions = []
        for doc in self.repository.list_documents():
            if doc.root_id == root_id:
                versions.append(doc)
        versions.sort(key=lambda d: d.version)
        return versions

    def search(
        self,
        text: str = "",
        client: str = "",
        occasion: str = "",
        products: str = "",
        date_from: str = "",
        date_to: str = "",
    ) -> List[ProposalDocument]:
        text = (text or "").lower()
        client = (client or "").lower()
        occasion = (occasion or "").lower()
        products = (products or "").lower()
        results: List[ProposalDocument] = []
        for doc in self.repository.list_documents():
            if client and client not in (doc.client or "").lower():
                continue
            if occasion and occasion not in (doc.intent.occasion or "").lower():
                continue
            if date_from and doc.created_at < date_from:
                continue
            if date_to and doc.created_at > date_to:
                continue
            if products:
                names = " ".join(i.name.lower() for i in doc.proposal.items)
                if products not in names:
                    continue
            if text:
                haystack = " ".join(
                    [
                        doc.original_query,
                        doc.proposal.name,
                        doc.proposal.commercial_description,
                        doc.client,
                        doc.intent.occasion or "",
                        doc.intent.target_audience or "",
                    ]
                    + [i.name for i in doc.proposal.items]
                ).lower()
                if text not in haystack:
                    continue
            results.append(doc)
        results.sort(key=lambda d: d.updated_at, reverse=True)
        return results
