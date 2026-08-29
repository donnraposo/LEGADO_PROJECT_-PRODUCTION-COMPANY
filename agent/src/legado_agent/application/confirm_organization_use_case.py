from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from legado_agent.application.ports.file_mover import FileMover
from legado_agent.application.ports.organization_repository import OrganizationRepository
from legado_agent.domain.analysis_batch import AnalysisBatch
from legado_agent.domain.analysis_item import AnalysisItem
from legado_agent.domain.organization_decision import OrganizationDecision
from legado_agent.domain.organization_item import OrganizationItem
from legado_agent.domain.organization_operation import OrganizationOperation


class ConfirmOrganizationUseCase:
    def __init__(self, repository: OrganizationRepository, file_mover: FileMover) -> None:
        self._repository = repository
        self._file_mover = file_mover

    def execute(
        self,
        batch: AnalysisBatch,
        items: list[AnalysisItem],
        decisions: list[OrganizationDecision],
    ) -> OrganizationOperation:
        if batch.status != "READY":
            raise ValueError("Somente uma prévia pronta pode ser confirmada.")
        if not batch.destination_root:
            raise ValueError("Selecione uma pasta-base e execute nova análise.")
        if self._repository.active_operation() is not None:
            raise ValueError("Já existe uma organização ativa nesta máquina.")
        selected = [item for item in items if item.selected]
        if not selected:
            raise ValueError("A prévia não possui arquivos selecionados.")
        decisions_by_item = {decision.analysis_item_id: decision for decision in decisions}
        operation = OrganizationOperation(
            id=uuid4(),
            batch_id=batch.id,
            company_id=batch.company_id,
            project_id=batch.project_id,
            destination_root=batch.destination_root,
            status="CONFIRMED",
            created_at=datetime.now(UTC),
        )
        organization_items = [
            self._prepare_item(operation, item, decisions_by_item.get(item.id)) for item in selected
        ]
        self._repository.create_operation(operation, organization_items)
        return operation

    def _prepare_item(
        self,
        operation: OrganizationOperation,
        item: AnalysisItem,
        decision: OrganizationDecision | None,
    ) -> OrganizationItem:
        action = decision.action if decision else "KEEP"
        resolved_name = decision.resolved_name if decision else ""
        if item.conflict_type and decision is None:
            raise ValueError(f"Resolva o conflito do arquivo {item.name}.")
        if action == "SKIP":
            return self._organization_item(
                operation, item, item.destination_path, action, "SKIPPED"
            )
        if action not in {"KEEP", "AUTO_RENAME", "RENAME"}:
            raise ValueError(f"Decisão inválida para {item.name}.")
        source = Path(item.source_path)
        self._file_mover.validate_source(source, item.size_bytes, item.source_modified_ns)
        destination = self._file_mover.choose_destination(
            Path(operation.destination_root),
            item.destination_path,
            action,
            resolved_name,
        )
        if source.absolute() == destination.absolute():
            raise ValueError(f"Origem e destino são iguais para {item.name}.")
        return self._organization_item(operation, item, str(destination), action, "PENDING")

    @staticmethod
    def _organization_item(
        operation: OrganizationOperation,
        item: AnalysisItem,
        destination_path: str,
        resolution: str,
        status: str,
    ) -> OrganizationItem:
        return OrganizationItem(
            id=uuid4(),
            operation_id=operation.id,
            analysis_item_id=item.id,
            source_path=item.source_path,
            destination_path=destination_path,
            checksum_sha256=item.checksum_sha256,
            size_bytes=item.size_bytes,
            source_modified_ns=item.source_modified_ns,
            resolution=resolution,
            status=status,
            error_message="",
            media_file_id=None,
        )
