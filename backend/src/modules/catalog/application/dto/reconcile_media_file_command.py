from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ReconcileMediaFileCommand:
    company_id: UUID
    media_file_id: UUID
    machine_id: UUID
    actor_user_id: UUID
    actor_role: str
    expected_version: int
    status: str
