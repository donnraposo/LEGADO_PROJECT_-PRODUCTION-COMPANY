import mimetypes
from collections.abc import Callable
from pathlib import Path
from uuid import UUID

from legado_agent.application.ports.backend_gateway import (
    BackendGateway,
    CatalogSyncConflictError,
    CatalogSyncError,
)
from legado_agent.application.ports.file_mover import FileMover
from legado_agent.application.ports.organization_repository import OrganizationRepository
from legado_agent.domain.organization_operation import OrganizationOperation

ProgressCallback = Callable[[int, int], None]
CancellationCheck = Callable[[], bool]


class ExecuteOrganizationUseCase:
    def __init__(
        self,
        repository: OrganizationRepository,
        file_mover: FileMover,
        backend: BackendGateway | None = None,
        machine_id: UUID | None = None,
    ) -> None:
        self._repository = repository
        self._file_mover = file_mover
        self._backend = backend
        self._machine_id = machine_id

    def execute(
        self,
        operation: OrganizationOperation,
        progress: ProgressCallback | None = None,
        cancelled: CancellationCheck | None = None,
    ) -> str:
        self._repository.update_operation_status(operation.id, "RUNNING")
        items = self._repository.list_items(operation.id)
        for position, item in enumerate(items, start=1):
            if cancelled and cancelled():
                self._repository.update_operation_status(operation.id, "INTERRUPTED")
                return "INTERRUPTED"
            if item.status in {"SKIPPED", "COPIED_SOURCE_REMAINS", "COMPLETED"}:
                if progress:
                    progress(position, len(items))
                continue
            if item.status in {"MOVED", "CATALOG_PENDING"}:
                self._sync_catalog(operation, item)
                if progress:
                    progress(position, len(items))
                continue
            try:
                if item.status == "MOVING":
                    reconciled = self._file_mover.reconcile(
                        Path(item.source_path),
                        Path(item.destination_path),
                        item.checksum_sha256,
                        item.size_bytes,
                    )
                    self._repository.update_item(item.id, reconciled)
                    if reconciled != "PENDING":
                        if reconciled == "MOVED":
                            self._sync_catalog(operation, item)
                        if progress:
                            progress(position, len(items))
                        continue
                self._file_mover.validate_source(
                    Path(item.source_path), item.size_bytes, item.source_modified_ns
                )
                self._repository.update_item(item.id, "MOVING")
                result = self._file_mover.move(
                    Path(item.source_path),
                    Path(item.destination_path),
                    item.checksum_sha256,
                    item.size_bytes,
                    item.id,
                )
                self._repository.update_item(item.id, result)
                if result == "MOVED":
                    self._sync_catalog(operation, item)
            except FileNotFoundError as exc:
                self._repository.update_item(item.id, "SOURCE_MISSING", str(exc))
            except FileExistsError as exc:
                self._repository.update_item(item.id, "DESTINATION_CONFLICT", str(exc))
            except OSError as exc:
                self._repository.update_item(item.id, "FAILED", str(exc))
            if progress:
                progress(position, len(items))
        final_items = self._repository.list_items(operation.id)
        clean = {"SKIPPED", "MOVED", "COMPLETED"}
        if any(item.status == "CATALOG_PENDING" for item in final_items):
            final_status = "INTERRUPTED"
        elif all(item.status in clean for item in final_items):
            final_status = "COMPLETED"
        else:
            final_status = "COMPLETED_WITH_WARNINGS"
        self._repository.update_operation_status(operation.id, final_status)
        return final_status

    def _sync_catalog(self, operation: OrganizationOperation, item) -> None:
        if self._backend is None or self._machine_id is None:
            return
        try:
            media_file_id = self._backend.ingest_media_file(
                operation.company_id,
                operation.project_id,
                self._machine_id,
                item.id,
                Path(item.destination_path).name,
                mimetypes.guess_type(item.destination_path)[0] or "",
                item.size_bytes,
                item.checksum_sha256,
            )
            self._repository.set_media_file_id(item.id, media_file_id)
        except CatalogSyncConflictError as exc:
            self._repository.update_item(item.id, "CATALOG_CONFLICT", str(exc))
        except CatalogSyncError as exc:
            self._repository.update_item(item.id, "CATALOG_PENDING", str(exc))
