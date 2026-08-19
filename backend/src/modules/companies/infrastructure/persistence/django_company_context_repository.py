from uuid import UUID

from modules.companies.application.dto.company_context_snapshot import CompanyContextSnapshot
from modules.companies.application.ports.company_context_repository import CompanyContextRepository
from modules.companies.domain.value_objects.membership_status import MembershipStatus
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel


class DjangoCompanyContextRepository(CompanyContextRepository):
    def find_active(self, company_id: UUID, user_id: UUID) -> CompanyContextSnapshot | None:
        model = (
            MembershipModel.objects.select_related("company")
            .filter(
                company_id=company_id,
                user_id=user_id,
                status=MembershipStatus.ACTIVE,
                company__archived_at__isnull=True,
            )
            .first()
        )
        if model is None:
            return None
        return CompanyContextSnapshot(
            membership_id=model.id,
            company_id=model.company_id,
            user_id=model.user_id,
            company_name=model.company.name,
            role=model.role,
        )
