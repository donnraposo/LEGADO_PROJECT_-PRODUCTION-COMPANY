from uuid import UUID

from modules.projects.application.dto.project_summary import ProjectSummary
from modules.projects.application.ports.project_repository import ProjectRepository


class ListProjectsUseCase:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    def execute(self, company_id: UUID, user_id: UUID, role: str) -> list[ProjectSummary]:
        return self._repository.list_active(company_id, user_id, role)
