from modules.companies.application.dto.company_membership_summary import (
    CompanyMembershipSummary,
)
from modules.companies.application.dto.create_company_command import CreateCompanyCommand
from modules.companies.application.ports.company_repository import CompanyRepository
from modules.companies.application.ports.membership_repository import MembershipRepository
from modules.companies.application.ports.unit_of_work import UnitOfWork
from modules.companies.domain.value_objects.company_name import CompanyName
from modules.companies.domain.value_objects.membership_role import MembershipRole


class CreateCompanyUseCase:
    def __init__(
        self,
        company_repository: CompanyRepository,
        membership_repository: MembershipRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._company_repository = company_repository
        self._membership_repository = membership_repository
        self._unit_of_work = unit_of_work

    def execute(self, command: CreateCompanyCommand) -> CompanyMembershipSummary:
        name = CompanyName(command.name)
        with self._unit_of_work:
            company = self._company_repository.create(name)
            self._membership_repository.add_owner(company.id, command.actor_user_id)
        return CompanyMembershipSummary(
            company_id=company.id,
            name=company.name,
            role=MembershipRole.OWNER,
            version=company.version,
        )
