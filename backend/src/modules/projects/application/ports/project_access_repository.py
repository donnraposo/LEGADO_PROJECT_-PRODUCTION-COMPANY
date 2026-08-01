from abc import ABC, abstractmethod
from uuid import UUID


class ProjectAccessRepository(ABC):
    @abstractmethod
    def active_project_exists(self, company_id: UUID, project_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    def grant(self, project_id: UUID, user_id: UUID) -> tuple[UUID, bool]:
        raise NotImplementedError

    @abstractmethod
    def revoke(self, project_id: UUID, user_id: UUID) -> UUID | None:
        raise NotImplementedError
