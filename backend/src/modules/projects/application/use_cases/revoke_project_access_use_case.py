from modules.projects.application.dto.change_project_access_command import (
    ChangeProjectAccessCommand,
)
from modules.projects.application.exceptions import ProjectNotFoundError
from modules.projects.application.ports.project_access_audit import ProjectAccessAudit
from modules.projects.application.ports.project_access_repository import ProjectAccessRepository
from modules.projects.application.ports.unit_of_work import UnitOfWork


class RevokeProjectAccessUseCase:
    def __init__(
        self,
        repository: ProjectAccessRepository,
        audit: ProjectAccessAudit,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._audit = audit
        self._unit_of_work = unit_of_work

    def execute(self, command: ChangeProjectAccessCommand) -> None:
        with self._unit_of_work:
            if not self._repository.active_project_exists(command.company_id, command.project_id):
                raise ProjectNotFoundError
            access_id = self._repository.revoke(command.project_id, command.administrator_user_id)
            if access_id is not None:
                self._audit.record_revoked(
                    company_id=command.company_id,
                    actor_user_id=command.actor_user_id,
                    access_id=access_id,
                    project_id=command.project_id,
                    user_id=command.administrator_user_id,
                )
