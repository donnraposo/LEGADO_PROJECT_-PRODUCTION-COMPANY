from pathlib import PurePath

from modules.catalog.application.dto.create_media_file_command import CreateMediaFileCommand
from modules.catalog.application.dto.media_file_summary import MediaFileSummary
from modules.catalog.application.exceptions import CatalogProjectAccessDeniedError
from modules.catalog.application.ports.catalog_repository import CatalogRepository
from modules.catalog.application.ports.project_catalog_authorization import (
    ProjectCatalogAuthorization,
)
from modules.catalog.application.ports.unit_of_work import UnitOfWork


class CreateMediaFileUseCase:
    def __init__(
        self,
        repository: CatalogRepository,
        authorization: ProjectCatalogAuthorization,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._authorization = authorization
        self._unit_of_work = unit_of_work

    def execute(self, command: CreateMediaFileCommand) -> MediaFileSummary:
        accessible = self._authorization.accessible_project_ids(
            command.company_id, command.actor_user_id, command.actor_role
        )
        if command.project_id not in accessible:
            raise CatalogProjectAccessDeniedError
        if not command.original_name.strip() or command.size_bytes < 0:
            raise ValueError("Invalid media file metadata")
        return self._create(command)

    def _create(self, command: CreateMediaFileCommand) -> MediaFileSummary:
        normalized = CreateMediaFileCommand(
            company_id=command.company_id,
            project_id=command.project_id,
            actor_user_id=command.actor_user_id,
            actor_role=command.actor_role,
            original_name=PurePath(command.original_name.strip().replace("\\", "/")).name,
            media_type=command.media_type.strip(),
            size_bytes=command.size_bytes,
            checksum_algorithm=command.checksum_algorithm.strip().upper(),
            checksum_digest=command.checksum_digest.strip().casefold(),
            recorded_at=command.recorded_at,
        )
        with self._unit_of_work:
            return self._repository.create(normalized)
