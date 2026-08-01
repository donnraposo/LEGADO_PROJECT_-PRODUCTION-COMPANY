from uuid import UUID

from modules.projects.application.ports.project_access_repository import (
    ProjectAccessRepository,
)
from modules.projects.infrastructure.persistence.models.project_access_model import (
    ProjectAccessModel,
)
from modules.projects.infrastructure.persistence.models.project_model import ProjectModel


class DjangoProjectAccessRepository(ProjectAccessRepository):
    def active_project_exists(self, company_id: UUID, project_id: UUID) -> bool:
        return ProjectModel.objects.filter(
            id=project_id,
            company_id=company_id,
            archived_at__isnull=True,
        ).exists()

    def grant(self, project_id: UUID, user_id: UUID) -> tuple[UUID, bool]:
        access, created = ProjectAccessModel.objects.get_or_create(
            project_id=project_id,
            user_id=user_id,
        )
        return access.id, created

    def revoke(self, project_id: UUID, user_id: UUID) -> UUID | None:
        access = ProjectAccessModel.objects.filter(
            project_id=project_id,
            user_id=user_id,
        ).first()
        if access is None:
            return None
        access_id = access.id
        access.delete()
        return access_id
