from abc import ABC, abstractmethod
from uuid import UUID

from legado_agent.domain.agent_command import AgentCommand
from legado_agent.domain.upload_job import UploadSession


class CatalogSyncError(Exception):
    pass


class CatalogSyncConflictError(CatalogSyncError):
    pass


class BackendOperationError(Exception):
    pass


class BackendGateway(ABC):
    @abstractmethod
    def upload_control(self, company_id: UUID, machine_id: UUID, item_id: UUID) -> str:
        raise NotImplementedError

    @abstractmethod
    def report_upload_state(
        self,
        company_id: UUID,
        machine_id: UUID,
        item_id: UUID,
        status: str,
        confirmed_bytes: int,
        failure_code: str = "",
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def ensure_upload_session(
        self, company_id: UUID, machine_id: UUID, item_id: UUID
    ) -> UploadSession:
        raise NotImplementedError

    @abstractmethod
    def record_upload_checkpoint(
        self, company_id: UUID, attempt_id: UUID, confirmed_bytes: int
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def confirm_upload_object(
        self, company_id: UUID, machine_id: UUID, attempt_id: UUID, provider_object_id: str
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def ingest_media_file(
        self,
        company_id: UUID,
        project_id: UUID,
        machine_id: UUID,
        ingestion_id: UUID,
        original_name: str,
        media_type: str,
        size_bytes: int,
        checksum_sha256: str,
    ) -> UUID:
        raise NotImplementedError

    @abstractmethod
    def list_companies(self) -> list[dict[str, object]]:
        raise NotImplementedError

    @abstractmethod
    def create_company(self, name: str) -> dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def list_clients(self, company_id: UUID) -> list[dict[str, object]]:
        raise NotImplementedError

    @abstractmethod
    def create_client(self, company_id: UUID, name: str) -> dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def list_projects(self, company_id: UUID) -> list[dict[str, object]]:
        raise NotImplementedError

    @abstractmethod
    def create_project(self, company_id: UUID, client_id: UUID, name: str) -> dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def heartbeat(
        self,
        company_id: UUID,
        installation_id: UUID,
        display_name: str,
        os_family: str,
        agent_version: str,
    ) -> UUID:
        raise NotImplementedError

    @abstractmethod
    def list_commands(
        self, company_id: UUID, machine_id: UUID, after_sequence: int
    ) -> list[AgentCommand]:
        raise NotImplementedError

    @abstractmethod
    def update_command(
        self,
        company_id: UUID,
        command: AgentCommand,
        status: str,
        *,
        progress_percent: int = 0,
        result: dict[str, object] | None = None,
        failure_code: str = "",
    ) -> AgentCommand:
        raise NotImplementedError
