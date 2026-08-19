from uuid import UUID

from modules.catalog.application.dto.tag_summary import TagSummary
from modules.catalog.application.exceptions import TagManagementDeniedError
from modules.catalog.application.ports.tag_repository import TagRepository
from modules.catalog.application.ports.unit_of_work import UnitOfWork
from modules.companies.domain.value_objects.membership_role import MembershipRole


class ListTagsUseCase:
    def __init__(self, repository: TagRepository) -> None:
        self._repository = repository

    def execute(self, company_id: UUID) -> list[TagSummary]:
        return self._repository.list_available(company_id)


class CreateCustomTagUseCase:
    def __init__(self, repository: TagRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    def execute(self, company_id: UUID, role: str, name: str) -> TagSummary:
        if role != MembershipRole.OWNER:
            raise TagManagementDeniedError
        normalized_name = " ".join(name.split())
        if not normalized_name:
            raise ValueError("Tag name is required")
        with self._unit_of_work:
            return self._repository.create_custom(company_id, normalized_name)


class ArchiveCustomTagUseCase:
    def __init__(self, repository: TagRepository, unit_of_work: UnitOfWork) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work

    def execute(self, company_id: UUID, role: str, tag_id: UUID) -> None:
        if role != MembershipRole.OWNER:
            raise TagManagementDeniedError
        with self._unit_of_work:
            self._repository.archive_custom(company_id, tag_id)
