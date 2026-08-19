from dataclasses import replace
from uuid import UUID, uuid4

from legado_agent.application.agent_coordinator import AgentCoordinator
from legado_agent.application.ports.backend_gateway import BackendGateway
from legado_agent.domain.agent_command import AgentCommand
from legado_agent.infrastructure.persistence.sqlite_database import SQLiteDatabase
from legado_agent.infrastructure.persistence.sqlite_local_repository import SQLiteLocalRepository


class FakeBackend(BackendGateway):
    def __init__(self, command: AgentCommand) -> None:
        self.machine_id = command.machine_id
        self.commands = [command]
        self.transitions: list[str] = []

    def ingest_media_file(
        self,
        company_id,
        project_id,
        machine_id,
        ingestion_id,
        original_name,
        media_type,
        size_bytes,
        checksum_sha256,
    ):
        return uuid4()

    def list_companies(self) -> list[dict[str, object]]:
        return []

    def list_clients(self, company_id) -> list[dict[str, object]]:
        return []

    def list_projects(self, company_id) -> list[dict[str, object]]:
        return []

    def heartbeat(self, company_id, installation_id, display_name, os_family, agent_version):
        return self.machine_id

    def list_commands(self, company_id, machine_id, after_sequence):
        return [command for command in self.commands if command.sequence > after_sequence]

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
        self.transitions.append(status)
        return replace(
            command,
            status=status,
            progress_percent=100 if status == "SUCCEEDED" else progress_percent,
            version=command.version + 1,
        )


def test_poll_acknowledges_runs_and_completes_ping(tmp_path) -> None:
    company_id = uuid4()
    machine_id = uuid4()
    command = AgentCommand(
        id=uuid4(),
        machine_id=machine_id,
        command_type="PING",
        resource_type="machine",
        resource_id=None,
        payload={},
        sequence=1,
        status="PENDING",
        progress_percent=0,
        version=1,
    )
    database = SQLiteDatabase(tmp_path / "agent.sqlite3")
    database.migrate()
    repository = SQLiteLocalRepository(database)
    backend = FakeBackend(command)
    coordinator = AgentCoordinator(repository, backend)

    coordinator.connect(company_id)
    assert coordinator.poll_once(company_id) == 1
    assert coordinator.poll_once(company_id) == 0

    assert backend.transitions == ["ACKNOWLEDGED", "RUNNING", "SUCCEEDED"]
    assert repository.machine_id(company_id) == machine_id
    assert repository.list_commands(company_id)[0].status == "SUCCEEDED"
