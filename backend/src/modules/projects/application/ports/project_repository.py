from abc import ABC, abstractmethod
from uuid import UUID

from modules.projects.application.dto.project_summary import ProjectSummary
from modules.projects.domain.value_objects.normalized_name import NormalizedName


class ProjectRepository(ABC):
    @abstractmethod
    def list_active(self, company_id: UUID, user_id: UUID, role: str) -> list[ProjectSummary]:
        raise NotImplementedError

    @abstractmethod
    def active_client_exists(self, company_id: UUID, client_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create(
        self, company_id: UUID, client_id: UUID, user_id: UUID, name: NormalizedName
    ) -> ProjectSummary:
        raise NotImplementedError

    @abstractmethod
    def grant_creator_access(self, project_id: UUID, user_id: UUID) -> None:
        raise NotImplementedError
