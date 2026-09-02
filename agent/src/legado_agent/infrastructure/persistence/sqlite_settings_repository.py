from pathlib import Path

from legado_agent.infrastructure.persistence.sqlite_database import SQLiteDatabase


class SQLiteSettingsRepository:
    ORGANIZATION_ROOT = "organization_root"

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def organization_root(self) -> Path | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT value FROM agent_settings WHERE key = ?",
                (self.ORGANIZATION_ROOT,),
            ).fetchone()
        return Path(row["value"]) if row and row["value"] else None

    def set_organization_root(self, root: Path) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO agent_settings(key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (self.ORGANIZATION_ROOT, str(root)),
            )
