from datetime import datetime
from uuid import UUID

from modules.companies.application.dto.accepted_membership import AcceptedMembership
from modules.companies.application.dto.invitation_snapshot import InvitationSnapshot
from modules.companies.application.ports.invitation_acceptance_repository import (
    InvitationAcceptanceRepository,
)
from modules.companies.infrastructure.persistence.models.invitation_model import InvitationModel
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel
from modules.identity.infrastructure.persistence.models.user_projection_model import (
    UserProjectionModel,
)


class DjangoInvitationAcceptanceRepository(InvitationAcceptanceRepository):
    def get_for_update(self, token_digest: str) -> InvitationSnapshot | None:
        model = (
            InvitationModel.objects.select_for_update().filter(token_digest=token_digest).first()
        )
        if model is None:
            return None
        return InvitationSnapshot(
            id=model.id,
            company_id=model.company_id,
            email_lookup_hmac=model.email_lookup_hmac,
            role=model.role,
            expires_at=model.expires_at,
            accepted_at=model.accepted_at,
            cancelled_at=model.cancelled_at,
        )

    def user_email_lookup(self, user_id: UUID) -> str:
        return UserProjectionModel.objects.values_list("email_lookup_hmac", flat=True).get(
            id=user_id
        )

    def activate_membership(self, company_id: UUID, user_id: UUID, role: str) -> AcceptedMembership:
        model, _ = MembershipModel.objects.update_or_create(
            company_id=company_id,
            user_id=user_id,
            defaults={"role": role, "status": "ACTIVE"},
        )
        return AcceptedMembership(
            id=model.id,
            company_id=model.company_id,
            role=model.role,
            status=model.status,
        )

    def mark_accepted(self, invitation_id: UUID, accepted_at: datetime) -> None:
        InvitationModel.objects.filter(id=invitation_id).update(accepted_at=accepted_at)
