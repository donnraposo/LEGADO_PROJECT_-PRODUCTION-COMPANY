from modules.projects.application.dto.client_summary import ClientSummary
from modules.projects.application.dto.create_client_command import CreateClientCommand
from modules.projects.application.ports.client_repository import ClientRepository
from modules.projects.application.ports.unit_of_work import UnitOfWork
from modules.projects.domain.value_objects.normalized_name import NormalizedName


class CreateClientUseCase:
    def __init__(self, repository: ClientRepository, unit_of_work: UnitOfWork) -> None:
        self._repository, self._unit_of_work = repository, unit_of_work

    def execute(self, command: CreateClientCommand) -> ClientSummary:
        with self._unit_of_work:
            return self._repository.create(command.company_id, NormalizedName(command.name))
