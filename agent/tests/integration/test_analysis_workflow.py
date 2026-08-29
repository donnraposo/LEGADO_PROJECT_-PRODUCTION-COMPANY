from uuid import uuid4

from legado_agent.application.analyze_selection_use_case import AnalyzeSelectionUseCase
from legado_agent.infrastructure.filesystem.safe_file_discovery import SafeFileDiscovery
from legado_agent.infrastructure.filesystem.streaming_sha256 import StreamingSha256
from legado_agent.infrastructure.filesystem.system_metadata_reader import SystemMetadataReader
from legado_agent.infrastructure.persistence.sqlite_analysis_repository import (
    SQLiteAnalysisRepository,
)
from legado_agent.infrastructure.persistence.sqlite_database import SQLiteDatabase


def test_analysis_is_read_only_detects_issues_and_survives_restart(tmp_path) -> None:
    source_a = tmp_path / "camera-a"
    source_b = tmp_path / "camera-b"
    source_a.mkdir()
    source_b.mkdir()
    first = source_a / "clip.mov"
    duplicate = source_a / "copy.mov"
    conflict = source_b / "clip.mov"
    first.write_bytes(b"first-content")
    duplicate.write_bytes(b"first-content")
    conflict.write_bytes(b"different-content")
    snapshots = {
        path: (path.read_bytes(), path.stat().st_mtime_ns) for path in (first, duplicate, conflict)
    }
    database = SQLiteDatabase(tmp_path / "agent.sqlite3")
    database.migrate()
    repository = SQLiteAnalysisRepository(database)
    use_case = _use_case(repository)
    company_id = uuid4()
    project_id = uuid4()
    progress: list[tuple[int, int]] = []

    batch, items = use_case.execute(
        company_id=company_id,
        client_name="Cliente",
        project_id=project_id,
        project_name="Projeto",
        selected_paths=[source_a, source_b],
        destination_root=tmp_path / "organized",
        progress=lambda current, total: progress.append((current, total)),
    )

    assert batch.status == "READY"
    assert len(items) == 3
    assert progress[-1] == (3, 3)
    assert any(item.conflict_type == "DUPLICATE_CONTENT" for item in items)
    assert any(item.conflict_type == "NAME_CONFLICT" for item in items)
    for path, (content, modified_at) in snapshots.items():
        assert path.read_bytes() == content
        assert path.stat().st_mtime_ns == modified_at

    restarted = SQLiteAnalysisRepository(database)
    restored_batch = restarted.latest_batch(company_id, project_id)
    assert restored_batch is not None
    assert restored_batch.status == "READY"
    restored_items = restarted.list_items(restored_batch.id)
    assert restored_items == items
    restarted.set_item_selected(restored_items[0].id, False)
    assert not restarted.list_items(restored_batch.id)[0].selected


def test_analysis_cancellation_preserves_partial_preview(tmp_path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "one.mov").write_bytes(b"one")
    (source / "two.mov").write_bytes(b"two")
    database = SQLiteDatabase(tmp_path / "agent.sqlite3")
    database.migrate()
    repository = SQLiteAnalysisRepository(database)
    processed = 0

    def progress(current: int, total: int) -> None:
        nonlocal processed
        processed = current

    batch, items = _use_case(repository).execute(
        company_id=uuid4(),
        client_name="Cliente",
        project_id=uuid4(),
        project_name="Projeto",
        selected_paths=[source],
        destination_root=tmp_path / "organized",
        progress=progress,
        cancelled=lambda: processed == 1,
    )

    assert batch.status == "CANCELLED"
    assert len(items) == 1


def _use_case(repository: SQLiteAnalysisRepository) -> AnalyzeSelectionUseCase:
    return AnalyzeSelectionUseCase(
        repository,
        SafeFileDiscovery(),
        SystemMetadataReader(),
        StreamingSha256(chunk_size=8),
    )
