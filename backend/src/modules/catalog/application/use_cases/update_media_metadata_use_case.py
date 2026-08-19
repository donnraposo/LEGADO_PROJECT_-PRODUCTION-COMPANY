from modules.catalog.application.dto.media_file_summary import MediaFileSummary
from modules.catalog.application.dto.update_media_metadata_command import (
    UpdateMediaMetadataCommand,
)
from modules.catalog.application.ports.catalog_audit import CatalogAudit
from modules.catalog.application.ports.catalog_repository import CatalogRepository
from modules.catalog.application.ports.project_catalog_authorization import (
    ProjectCatalogAuthorization,
)
from modules.catalog.application.ports.unit_of_work import UnitOfWork


class UpdateMediaMetadataUseCase:
    def __init__(
        self,
        repository: CatalogRepository,
        authorization: ProjectCatalogAuthorization,
        audit: CatalogAudit,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._authorization = authorization
        self._audit = audit
        self._unit_of_work = unit_of_work

    def execute(self, command: UpdateMediaMetadataCommand) -> MediaFileSummary:
        project_ids = self._authorization.accessible_project_ids(
            command.company_id, command.actor_user_id, command.actor_role
        )
        with self._unit_of_work:
            result = self._repository.update_metadata(command, project_ids)
            self._audit.record_metadata_updated(
                company_id=command.company_id,
                actor_user_id=command.actor_user_id,
                media_file_id=command.media_file_id,
                old_state=result.old_state,
                new_state=result.new_state,
            )
            return result.media_file
