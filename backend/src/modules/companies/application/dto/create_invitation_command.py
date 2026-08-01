from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateInvitationCommand:
    company_id: UUID
    company_name: str
    actor_user_id: UUID
    email: str
    role: str
    created_at: datetime
