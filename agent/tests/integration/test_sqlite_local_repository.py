from uuid import uuid4

from legado_agent.domain.agent_command import AgentCommand
from legado_agent.infrastructure.persistence.sqlite_database import SQLiteDatabase
from legado_agent.infrastructure.persistence.sqlite_local_repository import SQLiteLocalRepository


def test_installation_and_queue_survive_repository_restart(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "agent.sqlite3")
    database.migrate()
    first_repository = SQLiteLocalRepository(database)
    installation_id = first_repository.installation_id()
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
    first_repository.bind_machine(company_id, machine_id)
    first_repository.save_commands(company_id, [command, command])

    second_repository = SQLiteLocalRepository(database)

    assert second_repository.installation_id() == installation_id
    assert second_repository.machine_id(company_id) == machine_id
    assert second_repository.list_commands(company_id) == [command]
    assert second_repository.last_sequence(company_id) == 1


def test_database_schema_contains_no_token_or_password_column(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "agent.sqlite3")
    database.migrate()

    with database.connect() as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 3
        schema = " ".join(
            row["sql"] or ""
            for row in connection.execute(
                "SELECT sql FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        ).casefold()

    assert "token" not in schema
    assert "password" not in schema


def test_database_upgrades_existing_version_one_without_losing_installation(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "agent.sqlite3")
    with database.connect() as connection:
        connection.executescript(SQLiteDatabase._MIGRATIONS[0])
        connection.execute("PRAGMA user_version = 1")
        connection.execute(
            "INSERT INTO installation(singleton, installation_id) VALUES (1, ?)",
            (str(uuid4()),),
        )

    database.migrate()

    with database.connect() as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 3
        assert connection.execute("SELECT COUNT(*) FROM installation").fetchone()[0] == 1
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
    assert {
        "analysis_batches",
        "analysis_items",
        "organization_operations",
        "organization_items",
    } <= tables
