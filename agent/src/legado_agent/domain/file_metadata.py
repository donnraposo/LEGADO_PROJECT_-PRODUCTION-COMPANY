from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class FileMetadata:
    size_bytes: int
    modified_ns: int
    media_type: str
    file_date: date | None
    date_source: str
