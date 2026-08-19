from pathlib import Path

from legado_agent.application.ports.file_mover import FileMover
from legado_agent.application.ports.organization_repository import OrganizationRepository
from legado_agent.domain.organization_operation import OrganizationOperation


class ReconcileOrganizationUseCase:
    def __init__(self, repository: OrganizationRepository, file_mover: FileMover) -> None:
        self._repository = repository
        self._file_mover = file_mover

    def execute(self) -> OrganizationOperation | None:
        operation = self._repository.active_operation()
        if operation is None:
            return None
        self._repository.update_operation_status(operation.id, "INTERRUPTED")
        for item in self._repository.list_items(operation.id):
            if item.status != "MOVING":
                continue
            status = self._file_mover.reconcile(
                Path(item.source_path),
                Path(item.destination_path),
                item.checksum_sha256,
                item.size_bytes,
            )
            self._repository.update_item(item.id, status)
        return OrganizationOperation(
            id=operation.id,
            batch_id=operation.batch_id,
            company_id=operation.company_id,
            project_id=operation.project_id,
            destination_root=operation.destination_root,
            status="INTERRUPTED",
            created_at=operation.created_at,
        )
