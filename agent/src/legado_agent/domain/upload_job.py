from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UploadJob:
    item_id: UUID
    media_file_id: UUID
    source_path: str
    attempt_id: UUID
    size_bytes: int
    checksum_sha256: str
    confirmed_bytes: int
    status: str
    error_code: str = ""


@dataclass(frozen=True, slots=True)
class UploadSession:
    attempt_id: UUID
    item_id: UUID
    media_file_id: UUID
    session_url: str
    size_bytes: int
    checksum_sha256: str
    confirmed_bytes: int
