from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class OrganizationItem:
    id: UUID
    operation_id: UUID
    analysis_item_id: UUID
    source_path: str
    destination_path: str
    checksum_sha256: str
    size_bytes: int
    source_modified_ns: int
    resolution: str
    status: str
    error_message: str
    media_file_id: UUID | None
