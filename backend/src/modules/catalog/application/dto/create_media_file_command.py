from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateMediaFileCommand:
    company_id: UUID
    project_id: UUID
    actor_user_id: UUID
    actor_role: str
    original_name: str
    media_type: str
    size_bytes: int
    checksum_algorithm: str
    checksum_digest: str
    recorded_at: datetime | None
