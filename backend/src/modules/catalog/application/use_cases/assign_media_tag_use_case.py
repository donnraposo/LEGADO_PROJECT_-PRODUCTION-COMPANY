from uuid import UUID

from modules.catalog.application.ports.catalog_audit import CatalogAudit
from modules.catalog.application.ports.project_catalog_authorization import (
    ProjectCatalogAuthorization,
)
from modules.catalog.application.ports.tag_repository import TagRepository
from modules.catalog.application.ports.unit_of_work import UnitOfWork


class AssignMediaTagUseCase:
    def __init__(
        self,
        repository: TagRepository,
        authorization: ProjectCatalogAuthorization,
        audit: CatalogAudit,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._authorization = authorization
        self._audit = audit
        self._unit_of_work = unit_of_work

    def execute(
        self,
        *,
        company_id: UUID,
        media_file_id: UUID,
        tag_id: UUID,
        actor_user_id: UUID,
        actor_role: str,
    ) -> None:
        project_ids = self._authorization.accessible_project_ids(
            company_id, actor_user_id, actor_role
        )
        with self._unit_of_work:
            changed = self._repository.assign(
                company_id=company_id,
                media_file_id=media_file_id,
                tag_id=tag_id,
                actor_user_id=actor_user_id,
                project_ids=project_ids,
            )
            if changed:
                self._audit.record_tag_changed(
                    company_id=company_id,
                    actor_user_id=actor_user_id,
                    media_file_id=media_file_id,
                    tag_id=tag_id,
                    assigned=True,
                )


class RemoveMediaTagUseCase:
    def __init__(
        self,
        repository: TagRepository,
        authorization: ProjectCatalogAuthorization,
        audit: CatalogAudit,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._authorization = authorization
        self._audit = audit
        self._unit_of_work = unit_of_work

    def execute(
        self,
        *,
        company_id: UUID,
        media_file_id: UUID,
        tag_id: UUID,
        actor_user_id: UUID,
        actor_role: str,
    ) -> None:
        project_ids = self._authorization.accessible_project_ids(
            company_id, actor_user_id, actor_role
        )
        with self._unit_of_work:
            changed = self._repository.remove(
                company_id=company_id,
                media_file_id=media_file_id,
                tag_id=tag_id,
                project_ids=project_ids,
            )
            if changed:
                self._audit.record_tag_changed(
                    company_id=company_id,
                    actor_user_id=actor_user_id,
                    media_file_id=media_file_id,
                    tag_id=tag_id,
                    assigned=False,
                )
