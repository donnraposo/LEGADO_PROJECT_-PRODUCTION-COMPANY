import json
from datetime import date, datetime
from uuid import UUID

from legado_agent.application.ports.analysis_repository import AnalysisRepository
from legado_agent.domain.analysis_batch import AnalysisBatch
from legado_agent.domain.analysis_item import AnalysisItem
from legado_agent.infrastructure.persistence.sqlite_database import SQLiteDatabase


class SQLiteAnalysisRepository(AnalysisRepository):
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def create_batch(self, batch: AnalysisBatch) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO analysis_batches(
                    id, company_id, client_name, project_id, project_name,
                    source_paths_json, destination_root, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(batch.id),
                    str(batch.company_id),
                    batch.client_name,
                    str(batch.project_id),
                    batch.project_name,
                    json.dumps(batch.source_paths, ensure_ascii=False),
                    batch.destination_root,
                    batch.status,
                    batch.created_at.isoformat(),
                ),
            )

    def update_batch_status(self, batch_id: UUID, status: str) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                UPDATE analysis_batches
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, str(batch_id)),
            )

    def save_item(self, item: AnalysisItem) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO analysis_items(
                    id, batch_id, source_path, name, extension, media_type,
                    size_bytes, source_modified_ns, file_date, date_source, checksum_sha256,
                    destination_path, duplicate_of, conflict_type, warning, selected
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(item.id),
                    str(item.batch_id),
                    item.source_path,
                    item.name,
                    item.extension,
                    item.media_type,
                    item.size_bytes,
                    item.source_modified_ns,
                    item.file_date.isoformat() if item.file_date else None,
                    item.date_source,
                    item.checksum_sha256,
                    item.destination_path,
                    str(item.duplicate_of) if item.duplicate_of else None,
                    item.conflict_type,
                    item.warning,
                    int(item.selected),
                ),
            )

    def list_items(self, batch_id: UUID) -> list[AnalysisItem]:
        with self._database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM analysis_items WHERE batch_id = ? ORDER BY source_path",
                (str(batch_id),),
            ).fetchall()
        return [self._item(row) for row in rows]

    def latest_batch(self, company_id: UUID, project_id: UUID) -> AnalysisBatch | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM analysis_batches
                WHERE company_id = ? AND project_id = ?
                ORDER BY created_at DESC LIMIT 1
                """,
                (str(company_id), str(project_id)),
            ).fetchone()
        return self._batch(row) if row else None

    def set_item_selected(self, item_id: UUID, selected: bool) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                UPDATE analysis_items
                SET selected = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (int(selected), str(item_id)),
            )

    @staticmethod
    def _batch(row) -> AnalysisBatch:
        return AnalysisBatch(
            id=UUID(row["id"]),
            company_id=UUID(row["company_id"]),
            client_name=row["client_name"],
            project_id=UUID(row["project_id"]),
            project_name=row["project_name"],
            source_paths=tuple(json.loads(row["source_paths_json"])),
            destination_root=row["destination_root"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _item(row) -> AnalysisItem:
        return AnalysisItem(
            id=UUID(row["id"]),
            batch_id=UUID(row["batch_id"]),
            source_path=row["source_path"],
            name=row["name"],
            extension=row["extension"],
            media_type=row["media_type"],
            size_bytes=row["size_bytes"],
            source_modified_ns=row["source_modified_ns"],
            file_date=date.fromisoformat(row["file_date"]) if row["file_date"] else None,
            date_source=row["date_source"],
            checksum_sha256=row["checksum_sha256"],
            destination_path=row["destination_path"],
            duplicate_of=UUID(row["duplicate_of"]) if row["duplicate_of"] else None,
            conflict_type=row["conflict_type"],
            warning=row["warning"],
            selected=bool(row["selected"]),
        )
