from uuid import UUID

from modules.companies.application.dto.invitation_summary import InvitationSummary
from modules.companies.application.ports.invitation_query_repository import (
    InvitationQueryRepository,
)


class ListInvitationsUseCase:
    def __init__(self, repository: InvitationQueryRepository) -> None:
        self._repository = repository

    def execute(self, company_id: UUID) -> list[InvitationSummary]:
        return self._repository.list_for_company(company_id)
