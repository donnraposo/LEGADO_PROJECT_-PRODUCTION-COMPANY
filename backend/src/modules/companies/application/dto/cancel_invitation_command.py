from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CancelInvitationCommand:
    company_id: UUID
    actor_user_id: UUID
    invitation_id: UUID
    cancelled_at: datetime
