from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class InvitationCreationRepository(ABC):
    @abstractmethod
    def active_member_exists(self, company_id: UUID, email_lookup: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def cancel_pending_for_email(
        self, company_id: UUID, email_lookup: str, cancelled_at: datetime
    ) -> None:
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError
