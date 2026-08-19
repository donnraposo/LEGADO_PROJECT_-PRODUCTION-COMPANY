from uuid import UUID

from modules.companies.application.dto.membership_snapshot import MembershipSnapshot
from modules.companies.application.ports.membership_admin_repository import (
    MembershipAdminRepository,
)


class ListMembershipsUseCase:
    def __init__(self, repository: MembershipAdminRepository) -> None:
        self._repository = repository

    def execute(self, company_id: UUID) -> list[MembershipSnapshot]:
        return self._repository.list_for_company(company_id)
