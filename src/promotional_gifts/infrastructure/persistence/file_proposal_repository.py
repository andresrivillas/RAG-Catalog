import json
from pathlib import Path
from typing import List, Optional

from ...domain.entities.proposal_document import ProposalDocument
from ...domain.ports.proposal_repository_port import ProposalRepositoryPort
from ...domain.services.workspace.serializer import document_to_dict, dict_to_document


class FileProposalRepository(ProposalRepositoryPort):
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, proposal_id: str) -> Path:
        safe = proposal_id.replace("/", "_").replace("\\", "_")
        return self.base_dir / f"{safe}.json"

    def save(self, document: ProposalDocument) -> None:
        import datetime

        document.updated_at = datetime.datetime.now().isoformat(timespec="seconds")
        path = self._path(document.proposal_id)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(document_to_dict(document), fh, ensure_ascii=False, indent=2)

    def get(self, proposal_id: str) -> Optional[ProposalDocument]:
        path = self._path(proposal_id)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as fh:
            return dict_to_document(json.load(fh))

    def delete(self, proposal_id: str) -> None:
        path = self._path(proposal_id)
        if path.exists():
            path.unlink()

    def list_ids(self) -> List[str]:
        return [p.stem for p in sorted(self.base_dir.glob("*.json"))]

    def list_documents(self) -> List[ProposalDocument]:
        docs = []
        for pid in self.list_ids():
            doc = self.get(pid)
            if doc:
                docs.append(doc)
        return docs
