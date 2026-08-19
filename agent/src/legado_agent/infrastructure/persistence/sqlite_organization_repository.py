from datetime import datetime
from uuid import UUID

from legado_agent.application.ports.organization_repository import OrganizationRepository
from legado_agent.domain.organization_item import OrganizationItem
from legado_agent.domain.organization_operation import OrganizationOperation
from legado_agent.infrastructure.persistence.sqlite_database import SQLiteDatabase


class SQLiteOrganizationRepository(OrganizationRepository):
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def create_operation(
        self, operation: OrganizationOperation, items: list[OrganizationItem]
    ) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO organization_operations(
                    id, batch_id, company_id, project_id, destination_root,
                    status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(operation.id),
                    str(operation.batch_id),
                    str(operation.company_id),
                    str(operation.project_id),
                    operation.destination_root,
                    operation.status,
                    operation.created_at.isoformat(),
                ),
            )
            connection.executemany(
                """
                INSERT INTO organization_items(
                    id, operation_id, analysis_item_id, source_path,
                    destination_path, checksum_sha256, size_bytes,
                    source_modified_ns, resolution, status, error_message, media_file_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [self._item_values(item) for item in items],
            )

    def update_operation_status(self, operation_id: UUID, status: str) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                UPDATE organization_operations
                SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
                """,
                (status, str(operation_id)),
            )

    def update_item(
        self, item_id: UUID, status: str, error_message: str = ""
    ) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                UPDATE organization_items
                SET status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, error_message, str(item_id)),
            )

    def set_media_file_id(self, item_id: UUID, media_file_id: UUID) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                UPDATE organization_items
                SET media_file_id = ?, status = 'COMPLETED', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (str(media_file_id), str(item_id)),
            )

    def list_items(self, operation_id: UUID) -> list[OrganizationItem]:
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM organization_items
                WHERE operation_id = ? ORDER BY created_at, id
                """,
                (str(operation_id),),
            ).fetchall()
        return [self._item(row) for row in rows]

    def active_operation(self) -> OrganizationOperation | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM organization_operations
                WHERE status IN ('CONFIRMED', 'RUNNING', 'INTERRUPTED')
                ORDER BY created_at LIMIT 1
                """
            ).fetchone()
        return self._operation(row) if row else None

    @staticmethod
    def _item_values(item: OrganizationItem) -> tuple[object, ...]:
        return (
            str(item.id),
            str(item.operation_id),
            str(item.analysis_item_id),
            item.source_path,
            item.destination_path,
            item.checksum_sha256,
            item.size_bytes,
            item.source_modified_ns,
            item.resolution,
            item.status,
            item.error_message,
            str(item.media_file_id) if item.media_file_id else None,
        )

    @staticmethod
    def _operation(row) -> OrganizationOperation:
        return OrganizationOperation(
            id=UUID(row["id"]),
            batch_id=UUID(row["batch_id"]),
            company_id=UUID(row["company_id"]),
            project_id=UUID(row["project_id"]),
            destination_root=row["destination_root"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _item(row) -> OrganizationItem:
        return OrganizationItem(
            id=UUID(row["id"]),
            operation_id=UUID(row["operation_id"]),
            analysis_item_id=UUID(row["analysis_item_id"]),
            source_path=row["source_path"],
            destination_path=row["destination_path"],
            checksum_sha256=row["checksum_sha256"],
            size_bytes=row["size_bytes"],
            source_modified_ns=row["source_modified_ns"],
            resolution=row["resolution"],
            status=row["status"],
            error_message=row["error_message"],
            media_file_id=UUID(row["media_file_id"]) if row["media_file_id"] else None,
        )
