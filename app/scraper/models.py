from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class DocumentType(str, Enum):
    EXHIBITS = "Exhibits"
    KEY_DOCUMENTS = "Key Documents"
    OTHER_DOCUMENTS = "Other Documents"
    TRANSCRIPTS = "Transcripts"
    RECORDINGS = "Recordings"


@dataclass
class MatterCounts:
    exhibits: int = 0
    key_documents: int = 0
    other_documents: int = 0
    transcripts: int = 0
    recordings: int = 0

    def get(self, document_type: DocumentType) -> int:
        mapping = {
            DocumentType.EXHIBITS: self.exhibits,
            DocumentType.KEY_DOCUMENTS: self.key_documents,
            DocumentType.OTHER_DOCUMENTS: self.other_documents,
            DocumentType.TRANSCRIPTS: self.transcripts,
            DocumentType.RECORDINGS: self.recordings,
        }

        return mapping[document_type]


@dataclass
class MatterOverview:
    matter_number: str | None = None
    title_description: str | None = None
    type_value: str | None = None
    category_value: str | None = None
    date_received: str | None = None
    decision_date: str | None = None
    status: str | None = None
    outcome: str | None = None
    counts: MatterCounts = field(
        default_factory=MatterCounts
    )


@dataclass
class DownloadedDocument:
    saved_path: Path
    suggested_filename: str


@dataclass
class ScrapeResult:
    matter: MatterOverview
    requested_document_type: DocumentType
    downloaded: list[DownloadedDocument]