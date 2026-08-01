from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class InvitationSnapshot:
    id: UUID
    company_id: UUID
    email_lookup_hmac: str
    role: str
    expires_at: datetime
    accepted_at: datetime | None
    cancelled_at: datetime | None
