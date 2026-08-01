from abc import ABC, abstractmethod
from uuid import UUID


class ProjectAccessAudit(ABC):
    @abstractmethod
    def record_granted(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        access_id: UUID,
        project_id: UUID,
        user_id: UUID,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_revoked(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        access_id: UUID,
        project_id: UUID,
        user_id: UUID,
    ) -> None:
        raise NotImplementedError
