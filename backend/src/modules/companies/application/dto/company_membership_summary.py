from dataclasses import dataclass
from uuid import UUID

from modules.companies.domain.value_objects.membership_role import MembershipRole


@dataclass(frozen=True, slots=True)
class CompanyMembershipSummary:
    company_id: UUID
    name: str
    role: MembershipRole
    version: int
