from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AcceptInvitationCommand:
    user_id: UUID
    token: str
