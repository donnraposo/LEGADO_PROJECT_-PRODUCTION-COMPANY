import hashlib
from dataclasses import replace
from uuid import uuid4

import httpx
import pytest

from legado_agent.application.execute_upload_use_case import ExecuteUploadUseCase
from legado_agent.application.ports.resumable_upload_transport import (
    ChunkUploadResult,
    SessionExpiredError,
)
from legado_agent.domain.upload_job import UploadJob, UploadSession
from legado_agent.infrastructure.filesystem.streaming_sha256 import StreamingSha256
from legado_agent.infrastructure.http.http_resumable_upload_transport import (
    HttpResumableUploadTransport,
)
from legado_agent.infrastructure.persistence.sqlite_database import SQLiteDatabase
from legado_agent.infrastructure.persistence.sqlite_upload_repository import (
    SQLiteUploadRepository,
)


class FakeUploadRepository:
    def __init__(self, media_file_id, source_path) -> None:
        self.media_file_id = media_file_id
        self.path = str(source_path)
        self.job = None

    def source_path(self, media_file_id):
        return self.path if media_file_id == self.media_file_id else None

    def get(self, item_id):
        return self.job if self.job and self.job.item_id == item_id else None

    def save(self, job):
        self.job = job


class FakeBackend:
    def __init__(self, session) -> None:
        self.session = session
        self.session_calls = 0
        self.checkpoints = []
        self.confirmed_objects = []
        self.control = "UPLOADING"
        self.reported_states = []

    def upload_control(self, company_id, machine_id, item_id):
        return self.control

    def report_upload_state(
        self, company_id, machine_id, item_id, status, confirmed_bytes, failure_code=""
    ):
        self.reported_states.append((status, confirmed_bytes, failure_code))

    def ensure_upload_session(self, company_id, machine_id, item_id):
        self.session_calls += 1
        return replace(self.session, session_url=f"https://upload.test/{self.session_calls}")

    def record_upload_checkpoint(self, company_id, attempt_id, confirmed_bytes):
        self.checkpoints.append(confirmed_bytes)

    def confirm_upload_object(self, company_id, machine_id, attempt_id, provider_object_id):
        self.confirmed_objects.append(provider_object_id)


class FakeTransport:
    def __init__(self, expire_first=False) -> None:
        self.expire_first = expire_first
        self.calls = []

    def send_chunk(self, session_url, chunk, offset, total_bytes):
        self.calls.append((session_url, offset, len(chunk)))
        if self.expire_first:
            self.expire_first = False
            raise SessionExpiredError
        confirmed = offset + len(chunk)
        completed = confirmed == total_bytes
        return ChunkUploadResult(confirmed, completed, "drive-object" if completed else "")


def test_upload_sends_aligned_chunks_and_renews_expired_session(tmp_path) -> None:
    content = b"a" * (600 * 1024)
    source = tmp_path / "video.mov"
    source.write_bytes(content)
    item_id = uuid4()
    media_file_id = uuid4()
    session = UploadSession(
        attempt_id=uuid4(),
        item_id=item_id,
        media_file_id=media_file_id,
        session_url="https://upload.test/initial",
        size_bytes=len(content),
        checksum_sha256=hashlib.sha256(content).hexdigest(),
        confirmed_bytes=0,
    )
    repository = FakeUploadRepository(media_file_id, source)
    backend = FakeBackend(session)
    transport = FakeTransport(expire_first=True)

    result = ExecuteUploadUseCase(
        repository,
        backend,
        transport,
        StreamingSha256(),
        chunk_size=256 * 1024,
    ).execute(uuid4(), uuid4(), item_id)

    assert result.status == "SUCCEEDED"
    assert result.confirmed_bytes == len(content)
    assert backend.session_calls == 2
    assert backend.checkpoints == [256 * 1024, 512 * 1024, len(content)]
    assert backend.confirmed_objects == ["drive-object"]
    assert [call[2] for call in transport.calls] == [
        256 * 1024,
        256 * 1024,
        256 * 1024,
        88 * 1024,
    ]


def test_upload_pauses_before_next_chunk_without_regressing(tmp_path) -> None:
    content = b"a" * (600 * 1024)
    source = tmp_path / "video.mov"
    source.write_bytes(content)
    item_id, media_id, attempt_id = uuid4(), uuid4(), uuid4()
    backend = FakeBackend(
        UploadSession(
            attempt_id,
            item_id,
            media_id,
            "",
            len(content),
            hashlib.sha256(content).hexdigest(),
            256 * 1024,
        )
    )
    backend.control = "PAUSE_REQUESTED"
    repository = FakeUploadRepository(media_id, source)
    transport = FakeTransport()
    job = ExecuteUploadUseCase(
        repository, backend, transport, StreamingSha256(), chunk_size=256 * 1024
    ).execute(uuid4(), uuid4(), item_id)
    assert job.status == "PAUSED"
    assert job.confirmed_bytes == 256 * 1024
    assert transport.calls == []
    assert backend.reported_states == [("PAUSED", 256 * 1024, "")]


def test_drive_checkpoint_reconciles_stale_sqlite_before_next_chunk(tmp_path) -> None:
    content = b"a" * (768 * 1024)
    source = tmp_path / "video.mov"
    source.write_bytes(content)
    item_id, media_id = uuid4(), uuid4()
    repository = FakeUploadRepository(media_id, source)
    repository.job = UploadJob(
        item_id=item_id,
        media_file_id=media_id,
        source_path=str(source),
        attempt_id=uuid4(),
        size_bytes=len(content),
        checksum_sha256=hashlib.sha256(content).hexdigest(),
        confirmed_bytes=256 * 1024,
        status="INTERRUPTED",
    )
    backend = FakeBackend(
        UploadSession(
            uuid4(),
            item_id,
            media_id,
            "",
            len(content),
            hashlib.sha256(content).hexdigest(),
            512 * 1024,
        )
    )
    transport = FakeTransport()

    result = ExecuteUploadUseCase(
        repository, backend, transport, StreamingSha256(), chunk_size=256 * 1024
    ).execute(uuid4(), uuid4(), item_id)

    assert transport.calls[0][1] == 512 * 1024
    assert result.confirmed_bytes == len(content)


def test_sqlite_upload_checkpoint_survives_restart_without_session_url(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "agent.sqlite3")
    database.migrate()
    repository = SQLiteUploadRepository(database)
    job = UploadJob(
        item_id=uuid4(),
        media_file_id=uuid4(),
        source_path=str(tmp_path / "video.mov"),
        attempt_id=uuid4(),
        size_bytes=1000,
        checksum_sha256="a" * 64,
        confirmed_bytes=400,
        status="INTERRUPTED",
    )

    repository.save(job)
    restored = SQLiteUploadRepository(database).get(job.item_id)

    assert restored == job
    with database.connect() as connection:
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(upload_jobs)")}
    assert "session_url" not in columns


@pytest.mark.parametrize(
    ("status_code", "headers", "expected"),
    [
        (308, {"Range": "bytes=0-262143"}, ChunkUploadResult(262144, False)),
        (200, {}, ChunkUploadResult(300000, True, "object-1")),
    ],
)
def test_http_transport_interprets_drive_confirmation(status_code, headers, expected) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["content-range"] == "bytes 0-299999/300000"
        return httpx.Response(status_code, headers=headers, json={"id": "object-1"})

    transport = HttpResumableUploadTransport(transport=httpx.MockTransport(handler))
    assert transport.send_chunk("https://upload.test/session", b"x" * 300000, 0, 300000) == expected
    transport.close()
