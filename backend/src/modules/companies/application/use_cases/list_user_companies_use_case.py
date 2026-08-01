from uuid import UUID

from modules.companies.application.dto.company_membership_summary import (
    CompanyMembershipSummary,
)
from modules.companies.application.ports.company_repository import CompanyRepository


class ListUserCompaniesUseCase:
    def __init__(self, company_repository: CompanyRepository) -> None:
        self._company_repository = company_repository

    def execute(self, user_id: UUID) -> list[CompanyMembershipSummary]:
        return self._company_repository.list_active_for_user(user_id)
