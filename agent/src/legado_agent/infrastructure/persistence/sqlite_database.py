import sqlite3
from pathlib import Path


class SQLiteDatabase:
    _MIGRATIONS = (
        """
        CREATE TABLE installation (
            singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
            installation_id TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE machine_bindings (
            company_id TEXT PRIMARY KEY,
            machine_id TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE commands (
            id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL,
            machine_id TEXT NOT NULL,
            command_type TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            resource_id TEXT,
            payload_json TEXT NOT NULL,
            sequence INTEGER NOT NULL,
            status TEXT NOT NULL,
            progress_percent INTEGER NOT NULL DEFAULT 0,
            version INTEGER NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company_id, sequence)
        );
        CREATE INDEX ix_commands_company_status ON commands(company_id, status);
        """,
        """
        CREATE TABLE analysis_batches (
            id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL,
            client_name TEXT NOT NULL,
            project_id TEXT NOT NULL,
            project_name TEXT NOT NULL,
            source_paths_json TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX ix_analysis_batches_context
            ON analysis_batches(company_id, project_id, created_at DESC);
        CREATE TABLE analysis_items (
            id TEXT PRIMARY KEY,
            batch_id TEXT NOT NULL REFERENCES analysis_batches(id) ON DELETE CASCADE,
            source_path TEXT NOT NULL,
            name TEXT NOT NULL,
            extension TEXT NOT NULL,
            media_type TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            file_date TEXT,
            date_source TEXT NOT NULL,
            checksum_sha256 TEXT NOT NULL,
            destination_path TEXT NOT NULL,
            duplicate_of TEXT,
            conflict_type TEXT NOT NULL,
            warning TEXT NOT NULL,
            selected INTEGER NOT NULL CHECK (selected IN (0, 1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(batch_id, source_path)
        );
        CREATE INDEX ix_analysis_items_batch ON analysis_items(batch_id, destination_path);
        CREATE INDEX ix_analysis_items_checksum ON analysis_items(batch_id, checksum_sha256);
        """,
        """
        ALTER TABLE analysis_batches
            ADD COLUMN destination_root TEXT NOT NULL DEFAULT '';
        ALTER TABLE analysis_items
            ADD COLUMN source_modified_ns INTEGER NOT NULL DEFAULT 0;
        CREATE TABLE organization_operations (
            id TEXT PRIMARY KEY,
            batch_id TEXT NOT NULL UNIQUE REFERENCES analysis_batches(id),
            company_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            destination_root TEXT NOT NULL,
            active_slot INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE UNIQUE INDEX uq_active_organization
            ON organization_operations(active_slot)
            WHERE status IN ('CONFIRMED', 'RUNNING', 'INTERRUPTED');
        CREATE TABLE organization_items (
            id TEXT PRIMARY KEY,
            operation_id TEXT NOT NULL REFERENCES organization_operations(id) ON DELETE CASCADE,
            analysis_item_id TEXT NOT NULL UNIQUE REFERENCES analysis_items(id),
            source_path TEXT NOT NULL,
            destination_path TEXT NOT NULL,
            checksum_sha256 TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            source_modified_ns INTEGER NOT NULL,
            resolution TEXT NOT NULL,
            status TEXT NOT NULL,
            error_message TEXT NOT NULL DEFAULT '',
            media_file_id TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX ix_organization_items_operation_status
            ON organization_items(operation_id, status);
        """,
    )

    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def migrate(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            current = connection.execute("PRAGMA user_version").fetchone()[0]
            for version, migration in enumerate(self._MIGRATIONS, start=1):
                if version > current:
                    connection.executescript(migration)
                    connection.execute(f"PRAGMA user_version = {version}")
