from pathlib import PurePath

from modules.catalog.application.dto.ingest_media_file_command import IngestMediaFileCommand
from modules.catalog.application.dto.media_file_summary import MediaFileSummary
from modules.catalog.application.exceptions import (
    CatalogIngestionRaceError,
    CatalogProjectAccessDeniedError,
    MachineCatalogAccessDeniedError,
)
from modules.catalog.application.ports.catalog_repository import CatalogRepository
from modules.catalog.application.ports.machine_catalog_authorization import (
    MachineCatalogAuthorization,
)
from modules.catalog.application.ports.project_catalog_authorization import (
    ProjectCatalogAuthorization,
)
from modules.catalog.application.ports.unit_of_work import UnitOfWork


class IngestMediaFileUseCase:
    def __init__(
        self,
        repository: CatalogRepository,
        project_authorization: ProjectCatalogAuthorization,
        machine_authorization: MachineCatalogAuthorization,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._project_authorization = project_authorization
        self._machine_authorization = machine_authorization
        self._unit_of_work = unit_of_work

    def execute(self, command: IngestMediaFileCommand) -> tuple[MediaFileSummary, bool]:
        projects = self._project_authorization.accessible_project_ids(
            command.company_id, command.actor_user_id, command.actor_role
        )
        if command.project_id not in projects:
            raise CatalogProjectAccessDeniedError
        if not self._machine_authorization.is_registered_to_user(
            command.company_id, command.machine_id, command.actor_user_id
        ):
            raise MachineCatalogAccessDeniedError
        if not command.original_name.strip() or command.size_bytes < 0:
            raise ValueError("Invalid media file metadata")
        normalized = IngestMediaFileCommand(
            company_id=command.company_id,
            project_id=command.project_id,
            machine_id=command.machine_id,
            ingestion_id=command.ingestion_id,
            actor_user_id=command.actor_user_id,
            actor_role=command.actor_role,
            original_name=PurePath(command.original_name.strip().replace("\\", "/")).name,
            media_type=command.media_type.strip(),
            size_bytes=command.size_bytes,
            checksum_algorithm=command.checksum_algorithm.strip().upper(),
            checksum_digest=command.checksum_digest.strip().casefold(),
            recorded_at=command.recorded_at,
        )
        try:
            with self._unit_of_work:
                return self._repository.ingest(normalized)
        except CatalogIngestionRaceError:
            with self._unit_of_work:
                return self._repository.ingest(normalized)
