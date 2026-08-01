from uuid import UUID

from modules.companies.application.dto.company_membership_summary import (
    CompanyMembershipSummary,
)
from modules.companies.application.ports.company_repository import CompanyRepository
from modules.companies.domain.entities.company import Company
from modules.companies.domain.value_objects.company_name import CompanyName
from modules.companies.domain.value_objects.membership_role import MembershipRole
from modules.companies.domain.value_objects.membership_status import MembershipStatus
from modules.companies.infrastructure.persistence.models.company_model import CompanyModel


class DjangoCompanyRepository(CompanyRepository):
    def create(self, name: CompanyName) -> Company:
        model = CompanyModel.objects.create(name=name.value)
        return Company(
            id=model.id,
            name=model.name,
            archived_at=model.archived_at,
            version=model.version,
        )

    def list_active_for_user(self, user_id: UUID) -> list[CompanyMembershipSummary]:
        models = CompanyModel.objects.filter(
            archived_at__isnull=True,
            memberships__user_id=user_id,
            memberships__status=MembershipStatus.ACTIVE,
        ).values("id", "name", "version", "memberships__role")
        return [
            CompanyMembershipSummary(
                company_id=model["id"],
                name=model["name"],
                role=MembershipRole(model["memberships__role"]),
                version=model["version"],
            )
            for model in models
        ]
