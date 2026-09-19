from enum import Enum
from pydantic import BaseModel
from pathlib import Path

class DocumentType(Enum):
    EXHIBITS = "Exhibits"
    KEY_DOCUMENTS = "Key Documents"
    OTHER_DOCUMENTS = "Other Documents"
    TRANSCRIPTS = "Transcripts"
    RECORDINGS = "Recordings"

class MatterCounts(BaseModel):
    exhibits: int
    key_documents: int
    other_documents: int
    transcripts: int
    recordings: int

    def get(self, doc_type: DocumentType) -> int:
        return getattr(self, doc_type.name.lower())

class MatterOverview(BaseModel):
    matter_number: str
    counts: MatterCounts

class DownloadedDocument(BaseModel):
    saved_path: Path
    suggested_filename: str

class ScrapeResult(BaseModel):
    matter: MatterOverview
    requested_document_type: DocumentType
    downloaded: list[DownloadedDocument]
    raw_page_text: str # <--- Add this field