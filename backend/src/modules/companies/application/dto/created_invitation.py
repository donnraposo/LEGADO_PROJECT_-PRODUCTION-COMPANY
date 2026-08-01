from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreatedInvitation:
    id: UUID
    role: str
    expires_at: datetime
    token: str
