from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RestoreMetadataCommand:
    company_id: UUID
    media_file_id: UUID
    target_version: int
    expected_version: int
    actor_user_id: UUID
    actor_role: str
