from abc import ABC, abstractmethod
from uuid import UUID


class AuditEventRecorder(ABC):
    @abstractmethod
    def record_invitation_created(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        invitation_id: UUID,
        role: str,
        expires_at: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_invitation_cancelled(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        invitation_id: UUID,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_invitation_accepted(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        membership_id: UUID,
        role: str,
        status: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_membership_updated(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        membership_id: UUID,
        before: dict[str, object],
        after: dict[str, object],
    ) -> None:
        raise NotImplementedError
