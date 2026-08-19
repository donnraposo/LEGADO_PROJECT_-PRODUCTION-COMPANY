from uuid import UUID

from modules.projects.application.dto.client_summary import ClientSummary
from modules.projects.application.ports.client_repository import ClientRepository


class ListClientsUseCase:
    def __init__(self, repository: ClientRepository) -> None:
        self._repository = repository

    def execute(self, company_id: UUID) -> list[ClientSummary]:
        return self._repository.list_active(company_id)
