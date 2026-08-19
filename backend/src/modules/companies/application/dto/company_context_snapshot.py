from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CompanyContextSnapshot:
    membership_id: UUID
    company_id: UUID
    user_id: UUID
    company_name: str
    role: str
