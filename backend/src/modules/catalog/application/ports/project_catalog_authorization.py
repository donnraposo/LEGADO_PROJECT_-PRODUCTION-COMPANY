from abc import ABC, abstractmethod
from uuid import UUID


class ProjectCatalogAuthorization(ABC):
    @abstractmethod
    def accessible_project_ids(self, company_id: UUID, user_id: UUID, role: str) -> list[UUID]:
        raise NotImplementedError
