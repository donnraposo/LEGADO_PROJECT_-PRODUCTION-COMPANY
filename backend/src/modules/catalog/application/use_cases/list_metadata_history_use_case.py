from uuid import UUID

from modules.catalog.application.dto.metadata_version_summary import MetadataVersionSummary
from modules.catalog.application.ports.catalog_repository import CatalogRepository
from modules.catalog.application.ports.project_catalog_authorization import (
    ProjectCatalogAuthorization,
)


class ListMetadataHistoryUseCase:
    def __init__(
        self, repository: CatalogRepository, authorization: ProjectCatalogAuthorization
    ) -> None:
        self._repository = repository
        self._authorization = authorization

    def execute(
        self,
        company_id: UUID,
        media_file_id: UUID,
        user_id: UUID,
        role: str,
        *,
        after_version: int = 0,
        limit: int = 50,
    ) -> tuple[list[MetadataVersionSummary], int | None]:
        project_ids = self._authorization.accessible_project_ids(company_id, user_id, role)
        return self._repository.list_metadata_versions(
            company_id, media_file_id, project_ids, after_version, limit
        )
