from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UpdateMediaMetadataCommand:
    company_id: UUID
    media_file_id: UUID
    actor_user_id: UUID
    actor_role: str
    expected_version: int
    display_name: str | None
    description: str | None
    observations: str | None
    recorded_at: datetime | None
