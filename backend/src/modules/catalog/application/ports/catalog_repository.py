from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID

from modules.catalog.application.dto.create_media_file_command import CreateMediaFileCommand
from modules.catalog.application.dto.ingest_media_file_command import IngestMediaFileCommand
from modules.catalog.application.dto.media_file_query import MediaFileQuery
from modules.catalog.application.dto.media_file_state_update_result import (
    MediaFileStateUpdateResult,
)
from modules.catalog.application.dto.media_file_summary import MediaFileSummary
from modules.catalog.application.dto.metadata_restore_result import MetadataRestoreResult
from modules.catalog.application.dto.metadata_update_result import MetadataUpdateResult
from modules.catalog.application.dto.metadata_version_summary import MetadataVersionSummary
from modules.catalog.application.dto.reconcile_media_file_command import (
    ReconcileMediaFileCommand,
)
from modules.catalog.application.dto.restore_metadata_command import RestoreMetadataCommand
from modules.catalog.application.dto.update_media_metadata_command import (
    UpdateMediaMetadataCommand,
)


class CatalogRepository(ABC):
    @abstractmethod
    def create(self, command: CreateMediaFileCommand) -> MediaFileSummary:
        raise NotImplementedError

    @abstractmethod
    def ingest(self, command: IngestMediaFileCommand) -> tuple[MediaFileSummary, bool]:
        raise NotImplementedError

    @abstractmethod
    def list_active(self, query: MediaFileQuery) -> tuple[list[MediaFileSummary], UUID | None]:
        raise NotImplementedError

    @abstractmethod
    def update_metadata(
        self, command: UpdateMediaMetadataCommand, project_ids: Collection[UUID]
    ) -> MetadataUpdateResult:
        raise NotImplementedError

    @abstractmethod
    def reconcile_state(
        self, command: ReconcileMediaFileCommand, project_ids: Collection[UUID]
    ) -> MediaFileStateUpdateResult:
        raise NotImplementedError

    @abstractmethod
    def list_metadata_versions(
        self,
        company_id: UUID,
        media_file_id: UUID,
        project_ids: Collection[UUID],
        after_version: int,
        limit: int,
    ) -> tuple[list[MetadataVersionSummary], int | None]:
        raise NotImplementedError

    @abstractmethod
    def restore_metadata(
        self, command: RestoreMetadataCommand, project_ids: Collection[UUID]
    ) -> MetadataRestoreResult:
        raise NotImplementedError
