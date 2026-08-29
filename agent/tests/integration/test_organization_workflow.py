from pathlib import Path
from uuid import uuid4

import pytest

from legado_agent.application.analyze_selection_use_case import AnalyzeSelectionUseCase
from legado_agent.application.confirm_organization_use_case import ConfirmOrganizationUseCase
from legado_agent.application.execute_organization_use_case import ExecuteOrganizationUseCase
from legado_agent.application.ports.backend_gateway import CatalogSyncError
from legado_agent.application.reconcile_organization_use_case import ReconcileOrganizationUseCase
from legado_agent.infrastructure.filesystem.safe_file_discovery import SafeFileDiscovery
from legado_agent.infrastructure.filesystem.streaming_sha256 import StreamingSha256
from legado_agent.infrastructure.filesystem.system_metadata_reader import SystemMetadataReader
from legado_agent.infrastructure.filesystem.windows_safe_file_mover import (
    WindowsSafeFileMover,
)
from legado_agent.infrastructure.persistence.sqlite_analysis_repository import (
    SQLiteAnalysisRepository,
)
from legado_agent.infrastructure.persistence.sqlite_database import SQLiteDatabase
from legado_agent.infrastructure.persistence.sqlite_organization_repository import (
    SQLiteOrganizationRepository,
)


def test_confirmed_organization_moves_without_overwrite_and_checkpoints(tmp_path) -> None:
    source = tmp_path / "source" / "clip.mov"
    source.parent.mkdir()
    source.write_bytes(b"safe-content")
    batch, items, repository, mover = _analyze(tmp_path, source)
    operation = ConfirmOrganizationUseCase(repository, mover).execute(batch, items, [])

    status = ExecuteOrganizationUseCase(repository, mover).execute(operation)

    checkpoints = repository.list_items(operation.id)
    destination = Path(checkpoints[0].destination_path)
    assert status == "COMPLETED"
    assert checkpoints[0].status == "MOVED"
    assert not source.exists()
    assert destination.read_bytes() == b"safe-content"
    assert repository.active_operation() is None


def test_confirmation_rejects_changed_source_and_existing_destination(tmp_path) -> None:
    source = tmp_path / "source" / "clip.mov"
    source.parent.mkdir()
    source.write_bytes(b"before")
    batch, items, repository, mover = _analyze(tmp_path, source)
    source.write_bytes(b"after")

    with pytest.raises(OSError, match="mudou desde a prévia"):
        ConfirmOrganizationUseCase(repository, mover).execute(batch, items, [])

    source.write_bytes(b"before")
    source.touch()
    batch, items, repository, mover = _analyze(tmp_path, source)
    expected = Path(batch.destination_root).joinpath(
        *Path(items[0].destination_path.replace("\\", "/")).parts
    )
    expected.parent.mkdir(parents=True)
    expected.write_bytes(b"existing")
    with pytest.raises(FileExistsError, match="não será sobrescrito"):
        ConfirmOrganizationUseCase(repository, mover).execute(batch, items, [])


def test_reconciliation_recovers_move_completed_before_checkpoint(tmp_path) -> None:
    source = tmp_path / "source" / "clip.mov"
    source.parent.mkdir()
    source.write_bytes(b"safe-content")
    batch, items, repository, mover = _analyze(tmp_path, source)
    operation = ConfirmOrganizationUseCase(repository, mover).execute(batch, items, [])
    checkpoint = repository.list_items(operation.id)[0]
    repository.update_operation_status(operation.id, "RUNNING")
    repository.update_item(checkpoint.id, "MOVING")
    mover.move(
        source,
        Path(checkpoint.destination_path),
        checkpoint.checksum_sha256,
        checkpoint.size_bytes,
        checkpoint.id,
    )

    recovered = ReconcileOrganizationUseCase(repository, mover).execute()

    assert recovered is not None
    assert recovered.status == "INTERRUPTED"
    assert repository.list_items(operation.id)[0].status == "MOVED"


def test_verified_copy_path_preserves_content(tmp_path) -> None:
    source = tmp_path / "source.mov"
    destination = tmp_path / "destination.mov"
    content = b"cross-volume-simulation"
    source.write_bytes(content)
    checksum = StreamingSha256(chunk_size=3).calculate(source)
    mover = WindowsSafeFileMover(chunk_size=3)

    status = mover._copy_across_volumes(source, destination, checksum, len(content), uuid4())

    assert status == "MOVED"
    assert not source.exists()
    assert destination.read_bytes() == content


def test_cross_volume_copy_never_removes_preexisting_partial_file(tmp_path) -> None:
    source = tmp_path / "source.mov"
    destination = tmp_path / "destination.mov"
    transfer_id = uuid4()
    partial = destination.with_name(f".{destination.name}.{transfer_id}.legado-partial")
    source.write_bytes(b"new-content")
    partial.write_bytes(b"must-remain")
    checksum = StreamingSha256().calculate(source)

    with pytest.raises(FileExistsError):
        WindowsSafeFileMover()._copy_across_volumes(
            source, destination, checksum, source.stat().st_size, transfer_id
        )

    assert partial.read_bytes() == b"must-remain"
    assert source.exists()


def test_moved_file_is_cataloged_and_checkpointed(tmp_path) -> None:
    source = tmp_path / "source" / "clip.mov"
    source.parent.mkdir()
    source.write_bytes(b"catalog-content")
    batch, items, repository, mover = _analyze(tmp_path, source)
    operation = ConfirmOrganizationUseCase(repository, mover).execute(batch, items, [])
    media_file_id = uuid4()
    backend = _CatalogBackend(media_file_id)

    status = ExecuteOrganizationUseCase(repository, mover, backend, uuid4()).execute(operation)

    checkpoint = repository.list_items(operation.id)[0]
    assert status == "COMPLETED"
    assert checkpoint.status == "COMPLETED"
    assert checkpoint.media_file_id == media_file_id
    assert backend.ingestion_ids == [checkpoint.id]


def test_catalog_failure_keeps_operation_resumable_without_moving_twice(tmp_path) -> None:
    source = tmp_path / "source" / "clip.mov"
    source.parent.mkdir()
    source.write_bytes(b"retry-content")
    batch, items, repository, mover = _analyze(tmp_path, source)
    operation = ConfirmOrganizationUseCase(repository, mover).execute(batch, items, [])
    backend = _CatalogBackend(uuid4(), fail_once=True)
    use_case = ExecuteOrganizationUseCase(repository, mover, backend, uuid4())

    first_status = use_case.execute(operation)
    checkpoint = repository.list_items(operation.id)[0]
    destination = Path(checkpoint.destination_path)
    second_status = use_case.execute(operation)

    assert first_status == "INTERRUPTED"
    assert checkpoint.status == "CATALOG_PENDING"
    assert not source.exists()
    assert destination.exists()
    assert second_status == "COMPLETED"
    assert repository.list_items(operation.id)[0].status == "COMPLETED"
    assert backend.ingestion_ids == [checkpoint.id, checkpoint.id]


class _CatalogBackend:
    def __init__(self, media_file_id, *, fail_once: bool = False) -> None:
        self.media_file_id = media_file_id
        self.fail_once = fail_once
        self.ingestion_ids = []

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
        self.ingestion_ids.append(ingestion_id)
        if self.fail_once:
            self.fail_once = False
            raise CatalogSyncError("catálogo temporariamente indisponível")
        return self.media_file_id


def _analyze(tmp_path, source: Path):
    database = SQLiteDatabase(tmp_path / f"agent-{uuid4()}.sqlite3")
    database.migrate()
    analysis_repository = SQLiteAnalysisRepository(database)
    organization_repository = SQLiteOrganizationRepository(database)
    use_case = AnalyzeSelectionUseCase(
        analysis_repository,
        SafeFileDiscovery(),
        SystemMetadataReader(),
        StreamingSha256(chunk_size=3),
    )
    batch, items = use_case.execute(
        company_id=uuid4(),
        client_name="Cliente",
        project_id=uuid4(),
        project_name="Projeto",
        selected_paths=[source],
        destination_root=tmp_path / "organized",
    )
    return batch, items, organization_repository, WindowsSafeFileMover(chunk_size=3)
