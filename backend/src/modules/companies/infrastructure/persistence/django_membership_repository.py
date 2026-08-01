from uuid import UUID

from modules.companies.application.ports.membership_repository import MembershipRepository
from modules.companies.domain.value_objects.membership_role import MembershipRole
from modules.companies.domain.value_objects.membership_status import MembershipStatus
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel


class DjangoMembershipRepository(MembershipRepository):
    def add_owner(self, company_id: UUID, user_id: UUID) -> None:
        MembershipModel.objects.create(
            company_id=company_id,
            user_id=user_id,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
        )
