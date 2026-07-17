import tempfile
import unittest
from pathlib import Path

from promotional_gifts.domain.entities.commercial_intent import CommercialIntent
from promotional_gifts.domain.entities.commercial_proposal import CommercialProposal
from promotional_gifts.domain.services.workspace.proposal_workspace import (
    ProposalWorkspace,
)
from promotional_gifts.infrastructure.persistence.file_proposal_repository import (
    FileProposalRepository,
)


class ProposalWorkspacePersistenceTest(unittest.TestCase):
    def test_create_document_preserves_existing_proposal_id_and_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            repository = FileProposalRepository(Path(tmp))
            workspace = ProposalWorkspace(repository)
            proposal = CommercialProposal(
                name="PROPUESTA 2",
                score=80.0,
                proposal_id="prop-20260716-120000-abcd__v2",
            )

            document = workspace.create_document(
                proposal=proposal,
                intent=CommercialIntent(raw_text="Necesito regalos"),
                original_query="Necesito regalos",
            )
            loaded = repository.get("prop-20260716-120000-abcd__v2")

            self.assertEqual(document.proposal_id, "prop-20260716-120000-abcd__v2")
            self.assertEqual(document.version, 2)
            self.assertEqual(document.root_id, "prop-20260716-120000-abcd")
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.proposal.proposal_id, document.proposal_id)

    def test_create_document_still_generates_id_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repository = FileProposalRepository(Path(tmp))
            workspace = ProposalWorkspace(repository)
            proposal = CommercialProposal(name="PROPUESTA 1", score=80.0)

            document = workspace.create_document(
                proposal=proposal,
                intent=CommercialIntent(raw_text="Necesito regalos"),
                original_query="Necesito regalos",
            )

            self.assertTrue(document.proposal_id.startswith("prop-"))
            self.assertEqual(document.version, 1)
            self.assertEqual(proposal.proposal_id, document.proposal_id)


if __name__ == "__main__":
    unittest.main()
