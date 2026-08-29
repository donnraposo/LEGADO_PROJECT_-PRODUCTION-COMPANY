from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from modules.catalog.application.dto.tag_summary import TagSummary


@dataclass(frozen=True, slots=True)
class MediaFileSummary:
    id: UUID
    project_id: UUID
    original_name: str
    display_name: str
    media_type: str
    description: str
    observations: str
    size_bytes: int
    file_version_id: UUID
    source_machine_id: UUID | None
    checksum_algorithm: str
    checksum_digest: str
    recorded_at: datetime | None
    status: str
    version: int
    tags: tuple[TagSummary, ...] = ()
