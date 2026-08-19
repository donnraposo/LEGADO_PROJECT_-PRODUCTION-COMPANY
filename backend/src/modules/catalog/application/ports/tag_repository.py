from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID

from modules.catalog.application.dto.tag_summary import TagSummary


class TagRepository(ABC):
    @abstractmethod
    def list_available(self, company_id: UUID) -> list[TagSummary]:
        raise NotImplementedError

    @abstractmethod
    def create_custom(self, company_id: UUID, name: str) -> TagSummary:
        raise NotImplementedError

    @abstractmethod
    def archive_custom(self, company_id: UUID, tag_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def assign(
        self,
        *,
        company_id: UUID,
        media_file_id: UUID,
        tag_id: UUID,
        actor_user_id: UUID,
        project_ids: Collection[UUID],
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def remove(
        self,
        *,
        company_id: UUID,
        media_file_id: UUID,
        tag_id: UUID,
        project_ids: Collection[UUID],
    ) -> bool:
        raise NotImplementedError
