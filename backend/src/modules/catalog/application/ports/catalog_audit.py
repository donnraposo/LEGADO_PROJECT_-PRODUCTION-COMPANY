from abc import ABC, abstractmethod
from uuid import UUID


class CatalogAudit(ABC):
    @abstractmethod
    def record_metadata_updated(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        media_file_id: UUID,
        old_state: dict[str, object],
        new_state: dict[str, object],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_state_reconciled(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        media_file_id: UUID,
        machine_id: UUID,
        old_status: str,
        new_status: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_tag_changed(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        media_file_id: UUID,
        tag_id: UUID,
        assigned: bool,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_metadata_restored(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        media_file_id: UUID,
        target_version: int,
        old_state: dict[str, object],
        new_state: dict[str, object],
    ) -> None:
        raise NotImplementedError
