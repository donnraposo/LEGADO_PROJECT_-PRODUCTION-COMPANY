from uuid import UUID

from modules.companies.application.dto.invitation_summary import InvitationSummary
from modules.companies.application.ports.invitation_query_repository import (
    InvitationQueryRepository,
)
from modules.companies.infrastructure.persistence.models.invitation_model import InvitationModel


class DjangoInvitationQueryRepository(InvitationQueryRepository):
    def list_for_company(self, company_id: UUID) -> list[InvitationSummary]:
        invitations = InvitationModel.objects.filter(company_id=company_id)
        return [
            InvitationSummary(
                id=invitation.id,
                role=invitation.role,
                expires_at=invitation.expires_at,
                accepted_at=invitation.accepted_at,
                cancelled_at=invitation.cancelled_at,
            )
            for invitation in invitations
        ]
