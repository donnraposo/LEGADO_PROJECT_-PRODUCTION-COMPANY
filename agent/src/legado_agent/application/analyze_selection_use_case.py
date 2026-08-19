from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from legado_agent.application.destination_path_builder import build_destination_path
from legado_agent.application.ports.analysis_repository import AnalysisRepository
from legado_agent.application.ports.checksum_calculator import ChecksumCalculator
from legado_agent.application.ports.file_discovery import FileDiscovery
from legado_agent.application.ports.metadata_reader import MetadataReader
from legado_agent.domain.analysis_batch import AnalysisBatch
from legado_agent.domain.analysis_item import AnalysisItem

ProgressCallback = Callable[[int, int], None]
CancellationCheck = Callable[[], bool]


class AnalyzeSelectionUseCase:
    def __init__(
        self,
        repository: AnalysisRepository,
        discovery: FileDiscovery,
        metadata_reader: MetadataReader,
        checksum_calculator: ChecksumCalculator,
    ) -> None:
        self._repository = repository
        self._discovery = discovery
        self._metadata_reader = metadata_reader
        self._checksum_calculator = checksum_calculator

    def execute(
        self,
        *,
        company_id: UUID,
        client_name: str,
        project_id: UUID,
        project_name: str,
        selected_paths: list[Path],
        destination_root: Path,
        progress: ProgressCallback | None = None,
        cancelled: CancellationCheck | None = None,
    ) -> tuple[AnalysisBatch, list[AnalysisItem]]:
        if not selected_paths:
            raise ValueError("Selecione ao menos um arquivo ou pasta.")
        batch = AnalysisBatch(
            id=uuid4(),
            company_id=company_id,
            client_name=client_name,
            project_id=project_id,
            project_name=project_name,
            source_paths=tuple(str(path) for path in selected_paths),
            destination_root=str(destination_root),
            status="ANALYZING",
            created_at=datetime.now(UTC),
        )
        self._repository.create_batch(batch)
        paths = self._discovery.discover(selected_paths)
        checksums: dict[str, UUID] = {}
        destinations: dict[str, str] = {}
        for position, path in enumerate(paths, start=1):
            if cancelled and cancelled():
                batch = replace(batch, status="CANCELLED")
                self._repository.update_batch_status(batch.id, batch.status)
                return batch, self._repository.list_items(batch.id)
            item = self._analyze_file(batch, path, checksums, destinations)
            self._repository.save_item(item)
            if item.checksum_sha256:
                checksums.setdefault(item.checksum_sha256, item.id)
                destinations.setdefault(item.destination_path.casefold(), item.checksum_sha256)
            if progress:
                progress(position, len(paths))
        batch = replace(batch, status="READY")
        self._repository.update_batch_status(batch.id, batch.status)
        return batch, self._repository.list_items(batch.id)

    def _analyze_file(
        self,
        batch: AnalysisBatch,
        path: Path,
        checksums: dict[str, UUID],
        destinations: dict[str, str],
    ) -> AnalysisItem:
        item_id = uuid4()
        try:
            metadata = self._metadata_reader.read(path)
            checksum = self._checksum_calculator.calculate(path)
            destination = build_destination_path(
                batch.client_name, batch.project_name, metadata.file_date, path.name
            )
            duplicate_of = checksums.get(checksum)
            previous_checksum = destinations.get(destination.casefold())
            conflict_type = ""
            warnings: list[str] = []
            if duplicate_of:
                conflict_type = "DUPLICATE_CONTENT"
                warnings.append("Conteúdo duplicado encontrado na seleção.")
            if previous_checksum and previous_checksum != checksum:
                conflict_type = "NAME_CONFLICT"
                warnings.append("Outro arquivo usará o mesmo destino.")
            if metadata.file_date is None:
                warnings.append("Data de criação não identificada.")
            return AnalysisItem(
                id=item_id,
                batch_id=batch.id,
                source_path=str(path),
                name=path.name,
                extension=path.suffix.lstrip(".").casefold(),
                media_type=metadata.media_type,
                size_bytes=metadata.size_bytes,
                source_modified_ns=metadata.modified_ns,
                file_date=metadata.file_date,
                date_source=metadata.date_source,
                checksum_sha256=checksum,
                destination_path=destination,
                duplicate_of=duplicate_of,
                conflict_type=conflict_type,
                warning=" ".join(warnings),
                selected=True,
            )
        except OSError as exc:
            return AnalysisItem(
                id=item_id,
                batch_id=batch.id,
                source_path=str(path),
                name=path.name,
                extension=path.suffix.lstrip(".").casefold(),
                media_type="application/octet-stream",
                size_bytes=0,
                source_modified_ns=0,
                file_date=None,
                date_source="UNIDENTIFIED",
                checksum_sha256="",
                destination_path=build_destination_path(
                    batch.client_name, batch.project_name, None, path.name
                ),
                duplicate_of=None,
                conflict_type="ANALYSIS_ERROR",
                warning=str(exc),
                selected=False,
            )
