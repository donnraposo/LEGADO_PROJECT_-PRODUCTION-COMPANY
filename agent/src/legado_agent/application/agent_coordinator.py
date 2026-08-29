import platform
import socket
from uuid import UUID

from legado_agent.application.execute_upload_use_case import ExecuteUploadUseCase, UploadFileError
from legado_agent.application.ports.backend_gateway import BackendGateway
from legado_agent.application.ports.local_repository import LocalRepository


class AgentCoordinator:
    def __init__(
        self,
        repository: LocalRepository,
        backend: BackendGateway,
        upload_use_case: ExecuteUploadUseCase | None = None,
    ) -> None:
        self._repository = repository
        self._backend = backend
        self._upload_use_case = upload_use_case

    def connect(self, company_id: UUID) -> UUID:
        machine_id = self._backend.heartbeat(
            company_id=company_id,
            installation_id=self._repository.installation_id(),
            display_name=socket.gethostname(),
            os_family="WINDOWS" if platform.system() == "Windows" else platform.system().upper(),
            agent_version="0.1.0",
        )
        self._repository.bind_machine(company_id, machine_id)
        return machine_id

    def poll_once(self, company_id: UUID) -> int:
        machine_id = self.connect(company_id)
        commands = self._backend.list_commands(
            company_id, machine_id, self._repository.last_sequence(company_id)
        )
        self._repository.save_commands(company_id, commands)
        processed = 0
        for command in self._repository.list_commands(company_id):
            if command.status in {"SUCCEEDED", "FAILED", "CANCELLED"}:
                continue
            current = command
            if current.status == "PENDING":
                current = self._backend.update_command(company_id, current, "ACKNOWLEDGED")
                self._repository.update_command(company_id, current)
            if current.status == "ACKNOWLEDGED":
                current = self._backend.update_command(
                    company_id, current, "RUNNING", progress_percent=0
                )
                self._repository.update_command(company_id, current)
            if current.status == "RUNNING":
                if current.command_type == "PING":
                    current = self._backend.update_command(
                        company_id,
                        current,
                        "SUCCEEDED",
                        progress_percent=100,
                        result={"message": "pong"},
                    )
                elif (
                    current.command_type == "UPLOAD_FILE"
                    and current.resource_id is not None
                    and self._upload_use_case is not None
                ):
                    try:
                        job = self._upload_use_case.execute(
                            company_id, machine_id, current.resource_id
                        )
                        progress = (
                            int(job.confirmed_bytes * 100 / job.size_bytes) if job.size_bytes else 0
                        )
                        command_status = (
                            "SUCCEEDED"
                            if job.status == "SUCCEEDED"
                            else ("CANCELLED" if job.status == "CANCELLED" else "RUNNING")
                        )
                        current = self._backend.update_command(
                            company_id,
                            current,
                            command_status,
                            progress_percent=100 if job.status == "SUCCEEDED" else progress,
                            result={
                                "upload_item_id": str(job.item_id),
                                "confirmed_bytes": job.confirmed_bytes,
                                "state": job.status,
                            },
                        )
                    except UploadFileError as exc:
                        job = self._upload_use_case.repository.get(current.resource_id)
                        progress = (
                            int(job.confirmed_bytes * 100 / job.size_bytes)
                            if job and job.size_bytes
                            else current.progress_percent
                        )
                        current = self._backend.update_command(
                            company_id,
                            current,
                            "RUNNING",
                            progress_percent=progress,
                            result={"state": "INTERRUPTED"},
                            failure_code=str(exc)
                            if str(exc).isupper()
                            else (job.error_code if job else "INTERNET_UNAVAILABLE"),
                        )
                else:
                    current = self._backend.update_command(
                        company_id,
                        current,
                        "FAILED",
                        failure_code="UNSUPPORTED_COMMAND",
                    )
                self._repository.update_command(company_id, current)
                processed += 1
        return processed
