import json
import uuid
from uuid import UUID

from legado_agent.application.ports.local_repository import LocalRepository
from legado_agent.domain.agent_command import AgentCommand
from legado_agent.infrastructure.persistence.sqlite_database import SQLiteDatabase


class SQLiteLocalRepository(LocalRepository):
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def installation_id(self) -> UUID:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT installation_id FROM installation WHERE singleton = 1"
            ).fetchone()
            if row is None:
                value = uuid.uuid4()
                connection.execute(
                    "INSERT INTO installation(singleton, installation_id) VALUES (1, ?)",
                    (str(value),),
                )
                return value
            return UUID(row["installation_id"])

    def machine_id(self, company_id: UUID) -> UUID | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT machine_id FROM machine_bindings WHERE company_id = ?",
                (str(company_id),),
            ).fetchone()
        return UUID(row["machine_id"]) if row else None

    def bind_machine(self, company_id: UUID, machine_id: UUID) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO machine_bindings(company_id, machine_id) VALUES (?, ?)
                ON CONFLICT(company_id) DO UPDATE SET
                    machine_id = excluded.machine_id,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (str(company_id), str(machine_id)),
            )

    def save_commands(self, company_id: UUID, commands: list[AgentCommand]) -> None:
        with self._database.connect() as connection:
            for command in commands:
                connection.execute(
                    """
                    INSERT INTO commands(
                        id, company_id, machine_id, command_type, resource_type,
                        resource_id, payload_json, sequence, status, progress_percent, version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO NOTHING
                    """,
                    self._command_values(company_id, command),
                )

    def update_command(self, company_id: UUID, command: AgentCommand) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                UPDATE commands SET status = ?, progress_percent = ?, version = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND company_id = ?
                """,
                (
                    command.status,
                    command.progress_percent,
                    command.version,
                    str(command.id),
                    str(company_id),
                ),
            )

    def list_commands(self, company_id: UUID) -> list[AgentCommand]:
        with self._database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM commands WHERE company_id = ? ORDER BY sequence",
                (str(company_id),),
            ).fetchall()
        return [self._command(row) for row in rows]

    def last_sequence(self, company_id: UUID) -> int:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT COALESCE(MAX(sequence), 0) AS value FROM commands WHERE company_id = ?",
                (str(company_id),),
            ).fetchone()
        return int(row["value"])

    @staticmethod
    def _command_values(company_id: UUID, command: AgentCommand) -> tuple[object, ...]:
        return (
            str(command.id),
            str(company_id),
            str(command.machine_id),
            command.command_type,
            command.resource_type,
            str(command.resource_id) if command.resource_id else None,
            json.dumps(command.payload, sort_keys=True, separators=(",", ":")),
            command.sequence,
            command.status,
            command.progress_percent,
            command.version,
        )

    @staticmethod
    def _command(row) -> AgentCommand:
        return AgentCommand(
            id=UUID(row["id"]),
            machine_id=UUID(row["machine_id"]),
            command_type=row["command_type"],
            resource_type=row["resource_type"],
            resource_id=UUID(row["resource_id"]) if row["resource_id"] else None,
            payload=json.loads(row["payload_json"]),
            sequence=row["sequence"],
            status=row["status"],
            progress_percent=row["progress_percent"],
            version=row["version"],
        )
