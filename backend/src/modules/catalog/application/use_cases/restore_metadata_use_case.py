from modules.catalog.application.dto.media_file_summary import MediaFileSummary
from modules.catalog.application.dto.restore_metadata_command import RestoreMetadataCommand
from modules.catalog.application.exceptions import MetadataRestoreDeniedError
from modules.catalog.application.ports.catalog_audit import CatalogAudit
from modules.catalog.application.ports.catalog_repository import CatalogRepository
from modules.catalog.application.ports.project_catalog_authorization import (
    ProjectCatalogAuthorization,
)
from modules.catalog.application.ports.unit_of_work import UnitOfWork
from modules.companies.domain.value_objects.membership_role import MembershipRole


class RestoreMetadataUseCase:
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

    def execute(self, command: RestoreMetadataCommand) -> MediaFileSummary:
        if command.actor_role != MembershipRole.OWNER:
            raise MetadataRestoreDeniedError
        project_ids = self._authorization.accessible_project_ids(
            command.company_id, command.actor_user_id, command.actor_role
        )
        with self._unit_of_work:
            result = self._repository.restore_metadata(command, project_ids)
            if result.changed:
                self._audit.record_metadata_restored(
                    company_id=command.company_id,
                    actor_user_id=command.actor_user_id,
                    media_file_id=command.media_file_id,
                    target_version=result.target_version,
                    old_state=result.old_state,
                    new_state=result.new_state,
                )
            return result.media_file
