from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AnalysisItem:
    id: UUID
    batch_id: UUID
    source_path: str
    name: str
    extension: str
    media_type: str
    size_bytes: int
    source_modified_ns: int
    file_date: date | None
    date_source: str
    checksum_sha256: str
    destination_path: str
    duplicate_of: UUID | None
    conflict_type: str
    warning: str
    selected: bool
