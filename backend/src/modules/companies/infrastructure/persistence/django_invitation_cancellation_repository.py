from datetime import datetime
from uuid import UUID

from modules.companies.application.ports.invitation_cancellation_repository import (
    InvitationCancellationRepository,
)
from modules.companies.infrastructure.persistence.models.invitation_model import InvitationModel


class DjangoInvitationCancellationRepository(InvitationCancellationRepository):
    def cancel_pending(
        self,
        company_id: UUID,
        invitation_id: UUID,
        cancelled_at: datetime,
    ) -> bool:
        updated = InvitationModel.objects.filter(
            id=invitation_id,
            company_id=company_id,
            accepted_at__isnull=True,
            cancelled_at__isnull=True,
        ).update(cancelled_at=cancelled_at)
        return updated == 1
