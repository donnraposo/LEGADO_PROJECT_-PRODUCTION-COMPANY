from uuid import UUID

from modules.catalog.application.ports.project_catalog_authorization import (
    ProjectCatalogAuthorization,
)
from modules.companies.domain.value_objects.membership_role import MembershipRole
from modules.projects.infrastructure.persistence.models.project_model import ProjectModel


class DjangoProjectCatalogAuthorization(ProjectCatalogAuthorization):
    def accessible_project_ids(self, company_id: UUID, user_id: UUID, role: str) -> list[UUID]:
        projects = ProjectModel.objects.filter(company_id=company_id, archived_at__isnull=True)
        if role == MembershipRole.ADMINISTRATOR:
            projects = projects.filter(accesses__user_id=user_id)
        return list(projects.values_list("id", flat=True))
