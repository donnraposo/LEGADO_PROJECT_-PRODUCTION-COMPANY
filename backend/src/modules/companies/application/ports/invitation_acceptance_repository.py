from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from modules.companies.application.dto.accepted_membership import AcceptedMembership
from modules.companies.application.dto.invitation_snapshot import InvitationSnapshot


class InvitationAcceptanceRepository(ABC):
    @abstractmethod
    def get_for_update(self, token_digest: str) -> InvitationSnapshot | None:
        raise NotImplementedError

    @abstractmethod
    def user_email_lookup(self, user_id: UUID) -> str:
        raise NotImplementedError

    @abstractmethod
    def activate_membership(self, company_id: UUID, user_id: UUID, role: str) -> AcceptedMembership:
        raise NotImplementedError

    @abstractmethod
    def mark_accepted(self, invitation_id: UUID, accepted_at: datetime) -> None:
        raise NotImplementedError
