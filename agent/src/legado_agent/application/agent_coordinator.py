import platform
import socket
from uuid import UUID

from legado_agent.application.ports.backend_gateway import BackendGateway
from legado_agent.application.ports.local_repository import LocalRepository


class AgentCoordinator:
    def __init__(self, repository: LocalRepository, backend: BackendGateway) -> None:
        self._repository = repository
        self._backend = backend

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
                current = self._backend.update_command(
                    company_id, current, "ACKNOWLEDGED"
                )
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
