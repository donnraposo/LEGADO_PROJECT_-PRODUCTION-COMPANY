from uuid import UUID

from django.db import IntegrityError

from modules.companies.domain.value_objects.membership_role import MembershipRole
from modules.projects.application.dto.project_summary import ProjectSummary
from modules.projects.application.exceptions import ProjectNameConflictError
from modules.projects.application.ports.project_repository import ProjectRepository
from modules.projects.domain.value_objects.normalized_name import NormalizedName
from modules.projects.infrastructure.persistence.models.client_model import ClientModel
from modules.projects.infrastructure.persistence.models.project_access_model import (
    ProjectAccessModel,
)
from modules.projects.infrastructure.persistence.models.project_model import ProjectModel


class DjangoProjectRepository(ProjectRepository):
    def list_active(self, company_id: UUID, user_id: UUID, role: str) -> list[ProjectSummary]:
        items = ProjectModel.objects.filter(company_id=company_id, archived_at__isnull=True)
        if role == MembershipRole.ADMINISTRATOR:
            items = items.filter(accesses__user_id=user_id)
        return [self._summary(item) for item in items]

    def active_client_exists(self, company_id: UUID, client_id: UUID) -> bool:
        return ClientModel.objects.filter(
            id=client_id, company_id=company_id, archived_at__isnull=True
        ).exists()

    def create(
        self, company_id: UUID, client_id: UUID, user_id: UUID, name: NormalizedName
    ) -> ProjectSummary:
        try:
            item = ProjectModel.objects.create(
                company_id=company_id,
                client_id=client_id,
                name=name.value,
                normalized_name=name.normalized,
                created_by_user_id=user_id,
            )
        except IntegrityError as exc:
            raise ProjectNameConflictError from exc
        return self._summary(item)

    def grant_creator_access(self, project_id: UUID, user_id: UUID) -> None:
        ProjectAccessModel.objects.create(project_id=project_id, user_id=user_id)

    @staticmethod
    def _summary(item: ProjectModel) -> ProjectSummary:
        return ProjectSummary(item.id, item.client_id, item.name, item.version)
