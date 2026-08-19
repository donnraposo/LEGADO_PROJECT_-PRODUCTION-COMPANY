from modules.catalog.application.dto.media_file_summary import MediaFileSummary
from modules.catalog.application.dto.reconcile_media_file_command import (
    ReconcileMediaFileCommand,
)
from modules.catalog.application.exceptions import MachineCatalogAccessDeniedError
from modules.catalog.application.ports.catalog_audit import CatalogAudit
from modules.catalog.application.ports.catalog_repository import CatalogRepository
from modules.catalog.application.ports.machine_catalog_authorization import (
    MachineCatalogAuthorization,
)
from modules.catalog.application.ports.project_catalog_authorization import (
    ProjectCatalogAuthorization,
)
from modules.catalog.application.ports.unit_of_work import UnitOfWork


class ReconcileMediaFileUseCase:
    def __init__(
        self,
        repository: CatalogRepository,
        project_authorization: ProjectCatalogAuthorization,
        machine_authorization: MachineCatalogAuthorization,
        audit: CatalogAudit,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._project_authorization = project_authorization
        self._machine_authorization = machine_authorization
        self._audit = audit
        self._unit_of_work = unit_of_work

    def execute(self, command: ReconcileMediaFileCommand) -> MediaFileSummary:
        if not self._machine_authorization.is_registered_to_user(
            command.company_id, command.machine_id, command.actor_user_id
        ):
            raise MachineCatalogAccessDeniedError
        project_ids = self._project_authorization.accessible_project_ids(
            command.company_id, command.actor_user_id, command.actor_role
        )
        with self._unit_of_work:
            result = self._repository.reconcile_state(command, project_ids)
            if result.changed:
                self._audit.record_state_reconciled(
                    company_id=command.company_id,
                    actor_user_id=command.actor_user_id,
                    media_file_id=command.media_file_id,
                    machine_id=command.machine_id,
                    old_status=result.old_status,
                    new_status=result.new_status,
                )
            return result.media_file
