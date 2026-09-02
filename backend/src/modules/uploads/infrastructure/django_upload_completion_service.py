from uuid import UUID

from django.db import transaction
from django.utils import timezone

from modules.catalog.domain.media_file_status import MediaFileStatus
from modules.catalog.infrastructure.persistence.models import DriveObjectModel
from modules.projects.infrastructure.persistence.models.project_access_model import (
    ProjectAccessModel,
)
from modules.uploads.infrastructure.persistence.models import UploadAttemptModel, UploadBatchModel
from modules.uploads.infrastructure.upload_events import publish_upload_change


class DjangoUploadCompletionService:
    def __init__(self, protector, oauth_gateway, drive_gateway) -> None:
        self._protector = protector
        self._oauth = oauth_gateway
        self._drive = drive_gateway

    @transaction.atomic
    def complete(
        self,
        company_id: UUID,
        user_id: UUID,
        role: str,
        attempt_id: UUID,
        machine_id: UUID,
        provider_object_id: str,
    ) -> tuple[dict, bool]:
        attempt = (
            UploadAttemptModel.objects.select_for_update()
            .select_related(
                "item__batch__drive_account",
                "item__destination_folder",
                "item__file_version__media_file",
            )
            .filter(id=attempt_id, item__batch__company_id=company_id)
            .first()
        )
        if attempt is None or attempt.item.batch.machine_id != machine_id:
            raise ValueError("Tentativa não encontrada para esta máquina.")
        if (
            role == "ADMINISTRATOR"
            and not ProjectAccessModel.objects.filter(
                project_id=attempt.item.batch.project_id, user_id=user_id
            ).exists()
        ):
            raise ValueError("Tentativa não encontrada ou não autorizada.")
        existing = DriveObjectModel.objects.filter(upload_item=attempt.item).first()
        if existing:
            if existing.external_id != provider_object_id:
                raise ValueError("O item já foi confirmado com outro objeto.")
            return self._response(existing), False
        account = attempt.item.batch.drive_account
        if account.disconnected_at is not None or not account.refresh_token_ciphertext:
            raise ValueError("A conta vinculada ao lote não está disponível.")
        token = self._oauth.refresh_access_token(
            self._protector.decrypt(bytes(account.refresh_token_ciphertext))
        )
        remote = self._drive.get_object(token, provider_object_id)
        item = attempt.item
        if remote.get("trashed") or str(remote.get("size", "")) != str(item.size_bytes):
            raise ValueError("O objeto do Drive não possui o tamanho esperado ou está na lixeira.")
        if item.destination_folder.provider_folder_id not in remote.get("parents", []):
            raise ValueError("O objeto do Drive não está na pasta esperada.")
        if remote.get("name") != item.final_name:
            raise ValueError("O objeto do Drive não possui o nome esperado.")
        sha256 = str(remote.get("sha256Checksum", "")).casefold()
        if sha256 and sha256 != item.checksum_digest.casefold():
            raise ValueError("O checksum do objeto do Drive é divergente.")
        obj = DriveObjectModel.objects.create(
            upload_item=item,
            file_version=item.file_version,
            account=account,
            folder=item.destination_folder,
            external_id=provider_object_id,
            object_reference=provider_object_id,
            status="CONFIRMED",
            name=remote["name"],
            size_bytes=item.size_bytes,
            checksum_sha256=sha256,
            mime_type=remote.get("mimeType", ""),
        )
        attempt.status = "SUCCEEDED"
        attempt.completed_at = timezone.now()
        attempt.save(update_fields=["status", "completed_at", "updated_at"])
        item.status = "SUCCEEDED"
        item.save(update_fields=["status", "updated_at"])
        item.file_version.media_file.status = MediaFileStatus.SYNCHRONIZED
        item.file_version.media_file.save(update_fields=["status", "updated_at"])
        if not item.batch.items.exclude(status="SUCCEEDED").exists():
            UploadBatchModel.objects.filter(id=item.batch_id).update(status="SUCCEEDED")
        publish_upload_change(company_id, item.batch_id)
        return self._response(obj), True

    @staticmethod
    def _response(obj) -> dict:
        return {
            "id": str(obj.id),
            "upload_item_id": str(obj.upload_item_id),
            "provider_object_id": obj.external_id,
            "name": obj.name,
            "size_bytes": obj.size_bytes,
            "checksum_sha256": obj.checksum_sha256,
            "status": "CONFIRMED",
        }
