from modules.companies.domain.value_objects.membership_role import MembershipRole
from modules.projects.application.dto.create_project_command import CreateProjectCommand
from modules.projects.application.dto.project_summary import ProjectSummary
from modules.projects.application.exceptions import ClientNotFoundError
from modules.projects.application.ports.project_repository import ProjectRepository
from modules.projects.application.ports.unit_of_work import UnitOfWork
from modules.projects.domain.value_objects.normalized_name import NormalizedName


class CreateProjectUseCase:
    def __init__(self, repository: ProjectRepository, unit_of_work: UnitOfWork) -> None:
        self._repository, self._unit_of_work = repository, unit_of_work

    def execute(self, command: CreateProjectCommand) -> ProjectSummary:
        with self._unit_of_work:
            if not self._repository.active_client_exists(command.company_id, command.client_id):
                raise ClientNotFoundError
            project = self._repository.create(
                command.company_id,
                command.client_id,
                command.actor_user_id,
                NormalizedName(command.name),
            )
            if command.actor_role == MembershipRole.ADMINISTRATOR:
                self._repository.grant_creator_access(project.id, command.actor_user_id)
            return project
