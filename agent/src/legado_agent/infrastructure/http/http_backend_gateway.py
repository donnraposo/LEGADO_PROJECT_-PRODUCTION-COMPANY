from uuid import UUID

import httpx

from legado_agent.application.ports.backend_gateway import (
    BackendGateway,
    BackendOperationError,
    CatalogSyncConflictError,
    CatalogSyncError,
)
from legado_agent.domain.agent_command import AgentCommand
from legado_agent.domain.upload_job import UploadSession


class HttpBackendGateway(BackendGateway):
    def __init__(
        self,
        base_url: str,
        access_token: str,
        timeout: float = 15.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=timeout,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def ensure_upload_session(
        self, company_id: UUID, machine_id: UUID, item_id: UUID
    ) -> UploadSession:
        response = self._client.post(
            f"/api/v1/agent/upload-items/{item_id}/session",
            headers=self._company_headers(company_id),
            json={"machine_id": str(machine_id)},
        )
        self._raise_operation_error(response, "Não foi possível preparar o upload.")
        data = response.json()
        if str(data["checksum_algorithm"]).replace("-", "").upper() != "SHA256":
            raise BackendOperationError("O algoritmo de integridade não é compatível.")
        return UploadSession(
            attempt_id=UUID(data["attempt_id"]),
            item_id=UUID(data["item_id"]),
            media_file_id=UUID(data["media_file_id"]),
            session_url=str(data["session_url"]),
            size_bytes=int(data["size_bytes"]),
            checksum_sha256=str(data["checksum_digest"]).casefold(),
            confirmed_bytes=int(data["confirmed_bytes"]),
        )

    def upload_control(self, company_id: UUID, machine_id: UUID, item_id: UUID) -> str:
        response = self._client.get(
            f"/api/v1/agent/upload-items/{item_id}/control",
            headers=self._company_headers(company_id),
            params={"machine_id": str(machine_id)},
        )
        self._raise_operation_error(response, "Não foi possível consultar o controle do upload.")
        return str(response.json()["status"])

    def report_upload_state(
        self,
        company_id: UUID,
        machine_id: UUID,
        item_id: UUID,
        status: str,
        confirmed_bytes: int,
        failure_code: str = "",
    ) -> None:
        response = self._client.post(
            f"/api/v1/agent/upload-items/{item_id}/control",
            headers=self._company_headers(company_id),
            json={
                "machine_id": str(machine_id),
                "status": status,
                "confirmed_bytes": confirmed_bytes,
                "failure_code": failure_code,
            },
        )
        self._raise_operation_error(response, "Não foi possível confirmar o estado do upload.")

    def record_upload_checkpoint(
        self, company_id: UUID, attempt_id: UUID, confirmed_bytes: int
    ) -> None:
        response = self._client.put(
            f"/api/v1/upload-attempts/{attempt_id}/checkpoint",
            headers=self._company_headers(company_id),
            json={"confirmed_bytes": confirmed_bytes},
        )
        self._raise_operation_error(response, "Não foi possível confirmar o progresso.")

    def confirm_upload_object(
        self, company_id: UUID, machine_id: UUID, attempt_id: UUID, provider_object_id: str
    ) -> None:
        response = self._client.post(
            f"/api/v1/agent/upload-attempts/{attempt_id}/complete",
            headers=self._company_headers(company_id),
            json={"machine_id": str(machine_id), "provider_object_id": provider_object_id},
        )
        self._raise_operation_error(response, "Não foi possível confirmar o objeto do Drive.")

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
        response = self._client.post(
            "/api/v1/agent/media-files",
            headers=self._company_headers(company_id),
            json={
                "project_id": str(project_id),
                "machine_id": str(machine_id),
                "ingestion_id": str(ingestion_id),
                "original_name": original_name,
                "media_type": media_type,
                "size_bytes": size_bytes,
                "checksum_algorithm": "SHA256",
                "checksum_digest": checksum_sha256,
            },
        )
        if response.status_code == 409:
            raise CatalogSyncConflictError("O identificador local conflita com o catálogo.")
        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise CatalogSyncError("Não foi possível atualizar o catálogo central.") from exc
        return UUID(response.json()["id"])

    def list_companies(self) -> list[dict[str, object]]:
        response = self._client.get("/api/v1/companies")
        response.raise_for_status()
        return response.json()["items"]

    def create_company(self, name: str) -> dict[str, object]:
        response = self._client.post("/api/v1/companies", json={"name": name})
        self._raise_operation_error(response, "Não foi possível criar a empresa.")
        return response.json()

    def list_clients(self, company_id: UUID) -> list[dict[str, object]]:
        response = self._client.get("/api/v1/clients", headers=self._company_headers(company_id))
        response.raise_for_status()
        return response.json()["items"]

    def create_client(self, company_id: UUID, name: str) -> dict[str, object]:
        response = self._client.post(
            "/api/v1/clients",
            headers=self._company_headers(company_id),
            json={"name": name},
        )
        self._raise_operation_error(response, "Não foi possível criar o cliente.")
        return response.json()

    def list_projects(self, company_id: UUID) -> list[dict[str, object]]:
        response = self._client.get("/api/v1/projects", headers=self._company_headers(company_id))
        response.raise_for_status()
        return response.json()["items"]

    def create_project(self, company_id: UUID, client_id: UUID, name: str) -> dict[str, object]:
        response = self._client.post(
            "/api/v1/projects",
            headers=self._company_headers(company_id),
            json={"client_id": str(client_id), "name": name},
        )
        self._raise_operation_error(response, "Não foi possível criar o projeto.")
        return response.json()

    def heartbeat(
        self,
        company_id: UUID,
        installation_id: UUID,
        display_name: str,
        os_family: str,
        agent_version: str,
    ) -> UUID:
        response = self._client.post(
            "/api/v1/agent/machines/heartbeat",
            headers=self._company_headers(company_id),
            json={
                "installation_id": str(installation_id),
                "display_name": display_name,
                "os_family": os_family,
                "agent_version": agent_version,
            },
        )
        response.raise_for_status()
        return UUID(response.json()["id"])

    def list_commands(
        self, company_id: UUID, machine_id: UUID, after_sequence: int
    ) -> list[AgentCommand]:
        response = self._client.get(
            f"/api/v1/agent/machines/{machine_id}/commands",
            headers=self._company_headers(company_id),
            params={"after_sequence": after_sequence, "limit": 100},
        )
        response.raise_for_status()
        return [self._command(item) for item in response.json()["items"]]

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
        response = self._client.patch(
            f"/api/v1/agent/commands/{command.id}",
            headers=self._company_headers(company_id),
            json={
                "machine_id": str(command.machine_id),
                "expected_version": command.version,
                "status": status,
                "progress_percent": progress_percent,
                "result": result or {},
                "failure_code": failure_code,
            },
        )
        response.raise_for_status()
        return self._command(response.json())

    @staticmethod
    def _company_headers(company_id: UUID) -> dict[str, str]:
        return {"X-Company-ID": str(company_id)}

    @staticmethod
    def _raise_operation_error(response: httpx.Response, fallback: str) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            try:
                detail = str(response.json().get("detail", "")).strip()
            except (TypeError, ValueError):
                detail = ""
            raise BackendOperationError(detail or fallback) from exc

    @staticmethod
    def _command(item: dict[str, object]) -> AgentCommand:
        resource_id = item.get("resource_id")
        return AgentCommand(
            id=UUID(str(item["id"])),
            machine_id=UUID(str(item["machine_id"])),
            command_type=str(item["command_type"]),
            resource_type=str(item["resource_type"]),
            resource_id=UUID(str(resource_id)) if resource_id else None,
            payload=dict(item["payload"]),
            sequence=int(item["sequence"]),
            status=str(item["status"]),
            progress_percent=int(item["progress_percent"]),
            version=int(item["version"]),
        )
