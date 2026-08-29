from abc import ABC, abstractmethod
from uuid import UUID

from legado_agent.domain.organization_item import OrganizationItem
from legado_agent.domain.organization_operation import OrganizationOperation


class OrganizationRepository(ABC):
    @abstractmethod
    def create_operation(
        self, operation: OrganizationOperation, items: list[OrganizationItem]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_operation_status(self, operation_id: UUID, status: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_item(self, item_id: UUID, status: str, error_message: str = "") -> None:
        raise NotImplementedError

    @abstractmethod
    def set_media_file_id(self, item_id: UUID, media_file_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_items(self, operation_id: UUID) -> list[OrganizationItem]:
        raise NotImplementedError

    @abstractmethod
    def active_operation(self) -> OrganizationOperation | None:
        raise NotImplementedError
