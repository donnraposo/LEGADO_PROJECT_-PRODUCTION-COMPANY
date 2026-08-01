from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class MembershipSnapshot:
    id: UUID
    company_id: UUID
    user_id: UUID
    role: str
    status: str
    version: int
