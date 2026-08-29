import hashlib
import json
from datetime import date
from uuid import UUID

from django.db import IntegrityError, models, transaction

from modules.catalog.infrastructure.persistence.models.file_version_model import FileVersionModel
from modules.drive.infrastructure.persistence.models import DriveAccountModel, DriveFolderModel
from modules.operations.infrastructure.persistence.models.machine_model import MachineModel
from modules.projects.infrastructure.persistence.models.project_access_model import (
    ProjectAccessModel,
)
from modules.projects.infrastructure.persistence.models.project_model import ProjectModel
from modules.uploads.infrastructure.persistence.models import (
    UploadAttemptModel,
    UploadBatchModel,
    UploadCheckpointModel,
    UploadItemModel,
)


class UploadConflictError(ValueError):
    pass


class DjangoUploadService:
    TERMINAL_ATTEMPT_STATUSES = {"EXPIRED", "SUCCEEDED", "FAILED", "CANCELLED"}
    TERMINAL_ITEM_STATUSES = {"SUCCEEDED", "FAILED", "CANCELLED"}
    CONTROL_STATUS = {
        "PAUSE": "PAUSE_REQUESTED",
        "RESUME": "READY",
        "CANCEL": "CANCEL_REQUESTED",
    }

    @transaction.atomic
    def control_batch(self, company_id, user_id, role, batch_id, action, expected_version, key):
        batch = (
            UploadBatchModel.objects.select_for_update()
            .filter(id=batch_id, company_id=company_id)
            .first()
        )
        if batch is None:
            raise ValueError("Lote não encontrado.")
        self._require_project_access(batch.project_id, user_id, role)
        if batch.last_control_key == key:
            if batch.last_control_action != action:
                raise UploadConflictError("A chave de controle já foi usada em outra operação.")
            return self._batch_detail(batch)
        if batch.version != expected_version:
            raise UploadConflictError("O lote foi atualizado. Recarregue e tente novamente.")
        if batch.status in {"SUCCEEDED", "FAILED", "CANCELLED"}:
            raise UploadConflictError("O lote já foi concluído e não aceita novos controles.")
        target = self.CONTROL_STATUS[action]
        items = batch.items.exclude(status__in=self.TERMINAL_ITEM_STATUSES)
        items.update(
            status=target,
            last_control_key=key,
            last_control_action=action,
            version=models.F("version") + 1,
        )
        batch.status = target
        batch.last_control_key = key
        batch.last_control_action = action
        batch.version += 1
        batch.save(
            update_fields=[
                "status",
                "last_control_key",
                "last_control_action",
                "version",
                "updated_at",
            ]
        )
        return self._batch_detail(batch)

    def agent_control(self, company_id, machine_id, item_id) -> dict:
        item = UploadItemModel.objects.filter(
            id=item_id, batch__company_id=company_id, batch__machine_id=machine_id
        ).first()
        if item is None:
            raise ValueError("Item de upload não encontrado.")
        return {"item_id": str(item.id), "status": item.status, "version": item.version}

    @transaction.atomic
    def report_agent_state(
        self, company_id, machine_id, item_id, state, confirmed_bytes, failure_code=""
    ) -> dict:
        item = (
            UploadItemModel.objects.select_for_update()
            .filter(id=item_id, batch__company_id=company_id, batch__machine_id=machine_id)
            .first()
        )
        if item is None:
            raise ValueError("Item de upload não encontrado.")
        latest = self._confirmed_bytes(item)
        if confirmed_bytes < latest:
            raise UploadConflictError("O progresso não pode regredir.")
        allowed = {"PAUSED", "CANCELLED", "INTERRUPTED"}
        if state not in allowed:
            raise ValueError("Estado operacional inválido.")
        item.status = state
        item.version += 1
        item.save(update_fields=["status", "version", "updated_at"])
        active = item.attempts.filter(status__in=["CREATED", "ACTIVE", "INTERRUPTED"]).first()
        if active and state in {"CANCELLED", "INTERRUPTED"}:
            active.status = state
            active.failure_code = failure_code
            active.save(update_fields=["status", "failure_code", "updated_at"])
        batch = item.batch
        if (
            state == "PAUSED"
            and not batch.items.exclude(status__in=["PAUSED", "SUCCEEDED", "CANCELLED"]).exists()
        ):
            UploadBatchModel.objects.filter(id=batch.id).update(status="PAUSED")
        if (
            state == "CANCELLED"
            and not batch.items.exclude(status__in=["SUCCEEDED", "FAILED", "CANCELLED"]).exists()
        ):
            UploadBatchModel.objects.filter(id=batch.id).update(status="CANCELLED")
        return self._item(item)

    @transaction.atomic
    def create_batch(
        self,
        company_id: UUID,
        user_id: UUID,
        role: str,
        project_id: UUID,
        machine_id: UUID,
        folder_date: date,
        idempotency_key: str,
        items: list[dict],
    ) -> tuple[dict, bool]:
        normalized = {
            "project_id": str(project_id),
            "machine_id": str(machine_id),
            "date": folder_date.isoformat(),
            "items": [
                {
                    "file_version_id": str(item["file_version_id"]),
                    "destination_category": item["destination_category"],
                    "final_name": item["final_name"],
                }
                for item in items
            ],
        }
        digest = hashlib.sha256(
            json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        existing = UploadBatchModel.objects.filter(
            company_id=company_id, idempotency_key=idempotency_key
        ).first()
        if existing is not None:
            if existing.payload_digest != digest:
                raise UploadConflictError("A chave de idempotência já foi usada com outros dados.")
            return self._batch_detail(existing), False
        project = ProjectModel.objects.filter(
            id=project_id, company_id=company_id, archived_at__isnull=True
        ).first()
        if project is None or (
            role == "ADMINISTRATOR"
            and not ProjectAccessModel.objects.filter(project=project, user_id=user_id).exists()
        ):
            raise ValueError("Projeto não encontrado ou não autorizado.")
        machine = MachineModel.objects.filter(id=machine_id, company_id=company_id).first()
        if machine is None:
            raise ValueError("Máquina não encontrada na empresa ativa.")
        account = DriveAccountModel.objects.filter(
            company_id=company_id, disconnected_at__isnull=True
        ).first()
        if account is None:
            raise ValueError("Conecte uma conta Google antes de criar o lote.")
        version_ids = [item["file_version_id"] for item in items]
        versions = {
            version.id: version
            for version in FileVersionModel.objects.select_related("media_file").filter(
                id__in=version_ids,
                media_file__company_id=company_id,
                media_file__project_id=project_id,
                media_file__archived_at__isnull=True,
            )
        }
        if len(versions) != len(set(version_ids)) or len(version_ids) != len(set(version_ids)):
            raise ValueError("Um ou mais arquivos são inválidos ou repetidos.")
        month = folder_date.strftime("%Y.%m")
        day = folder_date.strftime("%d")
        requested_categories = {item["destination_category"] for item in items}
        folders = {
            category: DriveFolderModel.objects.filter(
                account=account,
                project=project,
                folder_key=f"project:{project.id}:day:{month}.{day}:{category.lower()}",
            ).first()
            for category in requested_categories
        }
        if any(folder is None for folder in folders.values()):
            raise ValueError("Prepare a árvore de pastas da data antes de criar o lote.")
        try:
            batch = UploadBatchModel.objects.create(
                company_id=company_id,
                project=project,
                machine=machine,
                drive_account=account,
                created_by_user_id=user_id,
                folder_date=folder_date,
                idempotency_key=idempotency_key,
                payload_digest=digest,
                total_items=len(items),
                total_bytes=sum(versions[item["file_version_id"]].size_bytes for item in items),
            )
            for position, item in enumerate(items, start=1):
                version = versions[item["file_version_id"]]
                UploadItemModel.objects.create(
                    batch=batch,
                    file_version=version,
                    destination_folder=folders[item["destination_category"]],
                    destination_category=item["destination_category"],
                    final_name=item["final_name"],
                    size_bytes=version.size_bytes,
                    checksum_algorithm=version.checksum_algorithm,
                    checksum_digest=version.checksum_digest,
                    position=position,
                )
        except IntegrityError as exc:
            raise UploadConflictError("Um arquivo já participa de outro lote ativo.") from exc
        return self._batch_detail(batch), True

    def list_batches(self, company_id: UUID, user_id: UUID, role: str) -> list[dict]:
        batches = UploadBatchModel.objects.filter(company_id=company_id)
        if role == "ADMINISTRATOR":
            batches = batches.filter(project__accesses__user_id=user_id)
        return [self._batch_summary(batch) for batch in batches.select_related("project")[:100]]

    def get_batch(self, company_id: UUID, user_id: UUID, role: str, batch_id: UUID) -> dict:
        batch = UploadBatchModel.objects.filter(id=batch_id, company_id=company_id).first()
        if batch is None or (
            role == "ADMINISTRATOR"
            and not ProjectAccessModel.objects.filter(
                project_id=batch.project_id, user_id=user_id
            ).exists()
        ):
            raise ValueError("Lote não encontrado ou não autorizado.")
        return self._batch_detail(batch)

    @transaction.atomic
    def create_attempt(
        self, company_id: UUID, user_id: UUID, role: str, item_id: UUID
    ) -> tuple[dict, bool]:
        item = (
            UploadItemModel.objects.select_for_update()
            .filter(id=item_id, batch__company_id=company_id)
            .first()
        )
        if item is None:
            raise ValueError("Item de upload não encontrado.")
        self._require_project_access(item.batch.project_id, user_id, role)
        active = item.attempts.filter(status__in=["CREATED", "ACTIVE", "INTERRUPTED"]).first()
        if active is not None:
            return self._attempt(active), False
        sequence = (
            item.attempts.order_by("-sequence").values_list("sequence", flat=True).first() or 0
        ) + 1
        attempt = UploadAttemptModel.objects.create(item=item, sequence=sequence)
        return self._attempt(attempt), True

    @transaction.atomic
    def record_checkpoint(
        self,
        company_id: UUID,
        user_id: UUID,
        role: str,
        attempt_id: UUID,
        confirmed_bytes: int,
    ) -> dict:
        attempt = (
            UploadAttemptModel.objects.select_for_update()
            .select_related("item__batch")
            .filter(id=attempt_id, item__batch__company_id=company_id)
            .first()
        )
        if attempt is None:
            raise ValueError("Tentativa de upload não encontrada.")
        self._require_project_access(attempt.item.batch.project_id, user_id, role)
        latest = attempt.checkpoints.order_by("-sequence").first()
        previous = latest.confirmed_bytes if latest else 0
        if confirmed_bytes < previous:
            raise UploadConflictError("O checkpoint não pode regredir.")
        if confirmed_bytes > attempt.item.size_bytes:
            raise ValueError("O checkpoint excede o tamanho do arquivo.")
        if latest is not None and confirmed_bytes == previous:
            return self._checkpoint(latest)
        checkpoint = UploadCheckpointModel.objects.create(
            attempt=attempt,
            sequence=(latest.sequence + 1 if latest else 1),
            confirmed_bytes=confirmed_bytes,
        )
        attempt.status = "ACTIVE"
        attempt.save(update_fields=["status", "updated_at"])
        UploadItemModel.objects.filter(id=attempt.item_id).exclude(
            status__in=["PAUSE_REQUESTED", "CANCEL_REQUESTED"]
        ).update(status="UPLOADING")
        UploadBatchModel.objects.filter(id=attempt.item.batch_id).exclude(
            status__in=["PAUSE_REQUESTED", "CANCEL_REQUESTED"]
        ).update(status="RUNNING")
        return self._checkpoint(checkpoint)

    @staticmethod
    def _require_project_access(project_id: UUID, user_id: UUID, role: str) -> None:
        if (
            role == "ADMINISTRATOR"
            and not ProjectAccessModel.objects.filter(
                project_id=project_id, user_id=user_id
            ).exists()
        ):
            raise ValueError("Recurso não encontrado ou não autorizado.")

    def _batch_detail(self, batch: UploadBatchModel) -> dict:
        result = self._batch_summary(batch)
        result["items"] = [self._item(item) for item in batch.items.all()]
        return result

    @staticmethod
    def _batch_summary(batch: UploadBatchModel) -> dict:
        items = list(batch.items.all())
        confirmed_bytes = sum(DjangoUploadService._confirmed_bytes(item) for item in items)
        progress_percent = (
            min(100, int(confirmed_bytes * 100 / batch.total_bytes)) if batch.total_bytes else 0
        )
        return {
            "id": str(batch.id),
            "project_id": str(batch.project_id),
            "machine_id": str(batch.machine_id),
            "drive_account_id": str(batch.drive_account_id),
            "folder_date": batch.folder_date.isoformat(),
            "status": batch.status,
            "total_items": batch.total_items,
            "total_bytes": batch.total_bytes,
            "confirmed_bytes": confirmed_bytes,
            "progress_percent": progress_percent,
            "version": batch.version,
            "created_at": batch.created_at.isoformat(),
        }

    @staticmethod
    def _item(item: UploadItemModel) -> dict:
        confirmed_bytes = DjangoUploadService._confirmed_bytes(item)
        return {
            "id": str(item.id),
            "file_version_id": str(item.file_version_id),
            "destination_folder_id": str(item.destination_folder_id),
            "destination_category": item.destination_category,
            "final_name": item.final_name,
            "size_bytes": item.size_bytes,
            "confirmed_bytes": confirmed_bytes,
            "progress_percent": (
                min(100, int(confirmed_bytes * 100 / item.size_bytes)) if item.size_bytes else 0
            ),
            "status": item.status,
            "position": item.position,
            "version": item.version,
        }

    @staticmethod
    def _confirmed_bytes(item: UploadItemModel) -> int:
        checkpoint = (
            UploadCheckpointModel.objects.filter(attempt__item=item)
            .order_by("-attempt__sequence", "-sequence")
            .values_list("confirmed_bytes", flat=True)
            .first()
        )
        return int(checkpoint or (item.size_bytes if item.status == "SUCCEEDED" else 0))

    @staticmethod
    def _attempt(attempt: UploadAttemptModel) -> dict:
        return {
            "id": str(attempt.id),
            "item_id": str(attempt.item_id),
            "sequence": attempt.sequence,
            "status": attempt.status,
        }

    @staticmethod
    def _checkpoint(checkpoint: UploadCheckpointModel) -> dict:
        return {
            "id": str(checkpoint.id),
            "attempt_id": str(checkpoint.attempt_id),
            "sequence": checkpoint.sequence,
            "confirmed_bytes": checkpoint.confirmed_bytes,
            "source": checkpoint.source,
        }
