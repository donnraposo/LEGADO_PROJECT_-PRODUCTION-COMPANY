from uuid import UUID

from modules.companies.domain.value_objects.membership_role import MembershipRole
from modules.companies.domain.value_objects.membership_status import MembershipStatus
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel
from modules.projects.application.ports.company_member_authorization import (
    CompanyMemberAuthorization,
)


class DjangoCompanyMemberAuthorization(CompanyMemberAuthorization):
    def is_active_administrator(self, company_id: UUID, user_id: UUID) -> bool:
        return MembershipModel.objects.filter(
            company_id=company_id,
            user_id=user_id,
            role=MembershipRole.ADMINISTRATOR,
            status=MembershipStatus.ACTIVE,
        ).exists()
