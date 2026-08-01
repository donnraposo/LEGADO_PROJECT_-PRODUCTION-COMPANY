from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UpdateMembershipCommand:
    company_id: UUID
    actor_user_id: UUID
    membership_id: UUID
    expected_version: int
    role: str | None
    status: str | None
