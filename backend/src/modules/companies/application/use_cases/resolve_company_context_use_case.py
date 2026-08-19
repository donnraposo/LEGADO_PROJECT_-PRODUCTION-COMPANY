from uuid import UUID

from modules.companies.application.dto.company_context_snapshot import CompanyContextSnapshot
from modules.companies.application.exceptions import CompanyAccessDeniedError, OwnerRequiredError
from modules.companies.application.ports.company_context_repository import CompanyContextRepository
from modules.companies.domain.value_objects.membership_role import MembershipRole


class ResolveCompanyContextUseCase:
    def __init__(self, repository: CompanyContextRepository) -> None:
        self._repository = repository

    def execute(
        self, company_id: UUID, user_id: UUID, *, owner_required: bool = False
    ) -> CompanyContextSnapshot:
        context = self._repository.find_active(company_id, user_id)
        if context is None:
            raise CompanyAccessDeniedError
        if owner_required and context.role != MembershipRole.OWNER:
            raise OwnerRequiredError
        return context
