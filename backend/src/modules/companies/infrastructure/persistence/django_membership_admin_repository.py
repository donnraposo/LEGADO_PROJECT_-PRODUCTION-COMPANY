from uuid import UUID

from modules.companies.application.dto.membership_snapshot import MembershipSnapshot
from modules.companies.application.ports.membership_admin_repository import (
    MembershipAdminRepository,
)
from modules.companies.domain.value_objects.membership_role import MembershipRole
from modules.companies.domain.value_objects.membership_status import MembershipStatus
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel


class DjangoMembershipAdminRepository(MembershipAdminRepository):
    def list_for_company(self, company_id: UUID) -> list[MembershipSnapshot]:
        return [
            self._snapshot(model)
            for model in MembershipModel.objects.filter(company_id=company_id).order_by(
                "created_at", "id"
            )
        ]

    def get_for_update(self, company_id: UUID, membership_id: UUID) -> MembershipSnapshot | None:
        model = (
            MembershipModel.objects.select_for_update()
            .filter(id=membership_id, company_id=company_id)
            .first()
        )
        return self._snapshot(model) if model else None

    def has_other_active_owner(self, company_id: UUID, membership_id: UUID) -> bool:
        return (
            MembershipModel.objects.filter(
                company_id=company_id,
                role=MembershipRole.OWNER,
                status=MembershipStatus.ACTIVE,
            )
            .exclude(id=membership_id)
            .exists()
        )

    def save(self, membership: MembershipSnapshot) -> None:
        MembershipModel.objects.filter(id=membership.id).update(
            role=membership.role,
            status=membership.status,
            version=membership.version,
        )

    @staticmethod
    def _snapshot(model: MembershipModel) -> MembershipSnapshot:
        return MembershipSnapshot(
            id=model.id,
            company_id=model.company_id,
            user_id=model.user_id,
            role=model.role,
            status=model.status,
            version=model.version,
        )
