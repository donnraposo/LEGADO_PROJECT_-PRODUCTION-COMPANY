from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AcceptedMembership:
    id: UUID
    company_id: UUID
    role: str
    status: str
