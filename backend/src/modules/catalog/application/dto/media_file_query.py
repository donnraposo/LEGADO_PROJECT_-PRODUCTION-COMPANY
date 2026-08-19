from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class MediaFileQuery:
    company_id: UUID
    project_ids: tuple[UUID, ...]
    search: str = ""
    project_id: UUID | None = None
    status: str = ""
    tag_id: UUID | None = None
    extension: str = ""
    media_type: str = ""
    min_size_bytes: int | None = None
    max_size_bytes: int | None = None
    recorded_from: datetime | None = None
    recorded_to: datetime | None = None
    created_by_user_id: UUID | None = None
    after_id: UUID | None = None
    limit: int = 50
