from uuid import UUID

from django.db import transaction
from django.utils import timezone

from modules.drive.infrastructure.google_drive_gateway import GoogleDriveGateway
from modules.drive.infrastructure.google_oauth_gateway import GoogleOAuthGateway
from modules.identity.infrastructure.cryptography.personal_data_protector import (
    PersonalDataProtector,
)
from modules.projects.infrastructure.persistence.models.project_access_model import (
    ProjectAccessModel,
)
from modules.uploads.infrastructure.persistence.models import (
    UploadAttemptModel,
    UploadCheckpointModel,
    UploadItemModel,
)


class DjangoUploadSessionService:
    def __init__(
        self,
        protector: PersonalDataProtector,
        oauth_gateway: GoogleOAuthGateway,
        drive_gateway: GoogleDriveGateway,
    ) -> None:
        self._protector = protector
        self._oauth_gateway = oauth_gateway
        self._drive_gateway = drive_gateway

    @transaction.atomic
    def ensure_session(
        self,
        company_id: UUID,
        user_id: UUID,
        role: str,
        item_id: UUID,
        machine_id: UUID,
    ) -> tuple[dict, bool]:
        item = (
            UploadItemModel.objects.select_for_update()
            .select_related(
                "batch__drive_account",
                "destination_folder",
                "file_version__media_file",
            )
            .filter(id=item_id, batch__company_id=company_id)
            .first()
        )
        if item is None or item.batch.machine_id != machine_id:
            raise ValueError("Item não encontrado para esta máquina.")
        if (
            role == "ADMINISTRATOR"
            and not ProjectAccessModel.objects.filter(
                project_id=item.batch.project_id, user_id=user_id
            ).exists()
        ):
            raise ValueError("Item não encontrado ou não autorizado.")

        completed = item.attempts.filter(status="SUCCEEDED").order_by("-sequence").first()
        if item.status == "VERIFYING" and completed is not None:
            session_url = self._protector.decrypt(bytes(completed.session_reference_ciphertext))
            return self._response(completed, session_url, item.size_bytes), False

        active = item.attempts.filter(status__in=["CREATED", "ACTIVE", "INTERRUPTED"]).first()
        if active is not None and active.session_reference_ciphertext:
            session_url = self._protector.decrypt(bytes(active.session_reference_ciphertext))
            state = self._drive_gateway.inspect_resumable_session(session_url, item.size_bytes)
            if state.status == "ACTIVE":
                self._persist_drive_checkpoint(active, state.confirmed_bytes)
                return self._response(active, session_url, state.confirmed_bytes), False
            if state.status == "COMPLETED":
                active.status = "SUCCEEDED"
                active.completed_at = timezone.now()
                active.save(update_fields=["status", "completed_at", "updated_at"])
                item.status = "VERIFYING"
                item.save(update_fields=["status", "updated_at"])
                self._persist_drive_checkpoint(active, item.size_bytes)
                return self._response(active, session_url, item.size_bytes), False
            active.status = "EXPIRED"
            active.failure_code = "SESSION_EXPIRED"
            active.completed_at = timezone.now()
            active.save(update_fields=["status", "failure_code", "completed_at", "updated_at"])
            active = None

        account = item.batch.drive_account
        if account.disconnected_at is not None or not account.refresh_token_ciphertext:
            raise ValueError("A conta do Drive vinculada ao lote não está disponível.")
        if active is None:
            sequence = (
                item.attempts.order_by("-sequence").values_list("sequence", flat=True).first() or 0
            ) + 1
            active = UploadAttemptModel.objects.create(item=item, sequence=sequence)

        refresh_token = self._protector.decrypt(bytes(account.refresh_token_ciphertext))
        access_token = self._oauth_gateway.refresh_access_token(refresh_token)
        content_type = item.file_version.media_file.media_type or "application/octet-stream"
        session_url = self._drive_gateway.create_resumable_session(
            access_token,
            item.destination_folder.provider_folder_id,
            item.final_name,
            item.size_bytes,
            content_type,
        )
        active.session_reference_ciphertext = self._protector.encrypt(session_url)
        active.status = "ACTIVE"
        active.started_at = active.started_at or timezone.now()
        active.failure_code = ""
        active.save(
            update_fields=[
                "session_reference_ciphertext",
                "status",
                "started_at",
                "failure_code",
                "updated_at",
            ]
        )
        item.status = "READY"
        item.save(update_fields=["status", "updated_at"])
        return self._response(active, session_url, 0), True

    @staticmethod
    def _persist_drive_checkpoint(attempt: UploadAttemptModel, confirmed_bytes: int) -> None:
        latest = attempt.checkpoints.order_by("-sequence").first()
        previous = latest.confirmed_bytes if latest else 0
        if confirmed_bytes <= previous:
            return
        UploadCheckpointModel.objects.create(
            attempt=attempt,
            sequence=(latest.sequence + 1 if latest else 1),
            confirmed_bytes=confirmed_bytes,
        )

    @staticmethod
    def _response(attempt: UploadAttemptModel, session_url: str, confirmed_bytes: int) -> dict:
        return {
            "attempt_id": str(attempt.id),
            "item_id": str(attempt.item_id),
            "sequence": attempt.sequence,
            "status": attempt.status,
            "session_url": session_url,
            "confirmed_bytes": confirmed_bytes,
            "media_file_id": str(attempt.item.file_version.media_file_id),
            "size_bytes": attempt.item.size_bytes,
            "checksum_algorithm": attempt.item.checksum_algorithm,
            "checksum_digest": attempt.item.checksum_digest,
        }
