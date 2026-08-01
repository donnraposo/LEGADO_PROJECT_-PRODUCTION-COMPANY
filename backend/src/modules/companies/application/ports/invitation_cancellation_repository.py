from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class InvitationCancellationRepository(ABC):
    @abstractmethod
    def cancel_pending(
        self,
        company_id: UUID,
        invitation_id: UUID,
        cancelled_at: datetime,
    ) -> bool:
        raise NotImplementedError
