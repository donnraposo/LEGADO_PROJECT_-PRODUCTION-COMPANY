from datetime import datetime
from uuid import UUID

from modules.companies.application.ports.invitation_creation_repository import (
    InvitationCreationRepository,
)
from modules.companies.infrastructure.persistence.models.invitation_model import InvitationModel
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel


class DjangoInvitationCreationRepository(InvitationCreationRepository):
    def active_member_exists(self, company_id: UUID, email_lookup: str) -> bool:
        return MembershipModel.objects.filter(
            company_id=company_id,
            user__email_lookup_hmac=email_lookup,
            status="ACTIVE",
        ).exists()

    def cancel_pending_for_email(
        self, company_id: UUID, email_lookup: str, cancelled_at: datetime
    ) -> None:
        InvitationModel.objects.filter(
            company_id=company_id,
            email_lookup_hmac=email_lookup,
            accepted_at__isnull=True,
            cancelled_at__isnull=True,
        ).update(cancelled_at=cancelled_at)

    def create(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        email_ciphertext: bytes,
        email_lookup: str,
        token_digest: str,
        role: str,
        expires_at: datetime,
    ) -> UUID:
        invitation = InvitationModel.objects.create(
            company_id=company_id,
            email_ciphertext=email_ciphertext,
            email_lookup_hmac=email_lookup,
            token_digest=token_digest,
            role=role,
            invited_by_user_id=actor_user_id,
            expires_at=expires_at,
        )
        return invitation.id
