from uuid import UUID

from legado_agent.application.ports.upload_repository import UploadRepository
from legado_agent.domain.upload_job import UploadJob
from legado_agent.infrastructure.persistence.sqlite_database import SQLiteDatabase


class SQLiteUploadRepository(UploadRepository):
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def source_path(self, media_file_id: UUID) -> str | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT destination_path FROM organization_items
                WHERE media_file_id = ? AND status = 'COMPLETED'
                ORDER BY updated_at DESC LIMIT 1
                """,
                (str(media_file_id),),
            ).fetchone()
        return row["destination_path"] if row else None

    def get(self, item_id: UUID) -> UploadJob | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM upload_jobs WHERE item_id = ?", (str(item_id),)
            ).fetchone()
        return self._job(row) if row else None

    def save(self, job: UploadJob) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO upload_jobs(
                    item_id, media_file_id, source_path, attempt_id, size_bytes,
                    checksum_sha256, confirmed_bytes, status, error_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(item_id) DO UPDATE SET
                    media_file_id = excluded.media_file_id,
                    source_path = excluded.source_path,
                    attempt_id = excluded.attempt_id,
                    size_bytes = excluded.size_bytes,
                    checksum_sha256 = excluded.checksum_sha256,
                    confirmed_bytes = excluded.confirmed_bytes,
                    status = excluded.status,
                    error_code = excluded.error_code,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    str(job.item_id),
                    str(job.media_file_id),
                    job.source_path,
                    str(job.attempt_id),
                    job.size_bytes,
                    job.checksum_sha256,
                    job.confirmed_bytes,
                    job.status,
                    job.error_code,
                ),
            )

    @staticmethod
    def _job(row) -> UploadJob:
        return UploadJob(
            item_id=UUID(row["item_id"]),
            media_file_id=UUID(row["media_file_id"]),
            source_path=row["source_path"],
            attempt_id=UUID(row["attempt_id"]),
            size_bytes=row["size_bytes"],
            checksum_sha256=row["checksum_sha256"],
            confirmed_bytes=row["confirmed_bytes"],
            status=row["status"],
            error_code=row["error_code"],
        )
