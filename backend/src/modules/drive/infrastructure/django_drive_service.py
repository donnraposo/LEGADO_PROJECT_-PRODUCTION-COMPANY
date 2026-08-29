import hashlib
import secrets
from datetime import date, timedelta
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from modules.drive.application.exceptions import InvalidOAuthStateError
from modules.drive.infrastructure.google_oauth_gateway import GoogleCredentials
from modules.drive.infrastructure.persistence.models import (
    DriveAccountModel,
    DriveFolderModel,
    DriveOAuthStateModel,
)
from modules.identity.infrastructure.cryptography.personal_data_protector import (
    PersonalDataProtector,
)
from modules.projects.infrastructure.persistence.models.project_model import ProjectModel


class DjangoDriveService:
    STATE_TTL = timedelta(minutes=10)

    def __init__(self, protector: PersonalDataProtector) -> None:
        self._protector = protector

    def create_state(self, company_id: UUID, user_id: UUID) -> str:
        raw_state = secrets.token_urlsafe(48)
        DriveOAuthStateModel.objects.create(
            state_digest=self._digest(raw_state),
            company_id=company_id,
            actor_user_id=user_id,
            expires_at=timezone.now() + self.STATE_TTL,
        )
        return raw_state

    @transaction.atomic
    def consume_state(self, raw_state: str) -> DriveOAuthStateModel:
        state = (
            DriveOAuthStateModel.objects.select_for_update()
            .filter(state_digest=self._digest(raw_state))
            .first()
        )
        now = timezone.now()
        if state is None or state.consumed_at is not None or state.expires_at <= now:
            raise InvalidOAuthStateError("Autorização expirada ou já utilizada.")
        state.consumed_at = now
        state.save(update_fields=["consumed_at"])
        return state

    def connect(self, state: DriveOAuthStateModel, credentials: GoogleCredentials) -> None:
        now = timezone.now()
        account = DriveAccountModel.objects.filter(
            company_id=state.company_id, disconnected_at__isnull=True
        ).first()
        values = {
            "connected_by_id": state.actor_user_id,
            "provider_account_id": credentials.provider_account_id,
            "email_ciphertext": self._protector.encrypt(credentials.email),
            "refresh_token_ciphertext": self._protector.encrypt(credentials.refresh_token),
            "granted_scopes": credentials.granted_scopes,
            "connected_at": now,
            "disconnected_at": None,
        }
        if account is None:
            DriveAccountModel.objects.create(company_id=state.company_id, **values)
        else:
            for field, value in values.items():
                setattr(account, field, value)
            account.save(update_fields=[*values, "updated_at"])

    def summary(self, company_id: UUID) -> dict:
        account = DriveAccountModel.objects.filter(
            company_id=company_id, disconnected_at__isnull=True
        ).first()
        if account is None:
            return {"connected": False, "account_email": None, "connected_at": None}
        return {
            "connected": True,
            "account_email": self._protector.decrypt(bytes(account.email_ciphertext)),
            "connected_at": account.connected_at.isoformat(),
        }

    def disconnect(self, company_id: UUID) -> None:
        DriveAccountModel.objects.filter(
            company_id=company_id, disconnected_at__isnull=True
        ).update(
            provider_account_id="",
            email_ciphertext=b"",
            refresh_token_ciphertext=b"",
            granted_scopes="",
            disconnected_at=timezone.now(),
        )

    @transaction.atomic
    def ensure_folder_tree(
        self,
        company_id: UUID,
        project_id: UUID,
        folder_date: date,
        oauth_gateway,
        drive_gateway,
    ) -> dict[str, object]:
        account = (
            DriveAccountModel.objects.select_for_update()
            .filter(company_id=company_id, disconnected_at__isnull=True)
            .first()
        )
        if account is None:
            raise ValueError("Conecte uma conta Google antes de preparar as pastas.")
        project = (
            ProjectModel.objects.select_related("company")
            .filter(
                id=project_id,
                company_id=company_id,
                archived_at__isnull=True,
            )
            .first()
        )
        if project is None:
            raise ValueError("Projeto não encontrado na empresa ativa.")
        refresh_token = self._protector.decrypt(bytes(account.refresh_token_ciphertext))
        access_token = oauth_gateway.refresh_access_token(refresh_token)
        date_segment = folder_date.strftime("%Y.%m")
        day_segment = folder_date.strftime("%d")
        definitions = [
            ("root", "Gerenciador de Áudio Visual", None),
            ("company", self._safe_name(project.company.name), None),
            (f"project:{project.id}", self._safe_name(project.name), project),
            (f"project:{project.id}:month:{date_segment}", date_segment, project),
            (f"project:{project.id}:day:{date_segment}.{day_segment}", day_segment, project),
        ]
        parent_id = "root"
        for folder_key, name, related_project in definitions:
            parent_id = self._ensure_folder(
                account, related_project, folder_key, name, parent_id, access_token, drive_gateway
            )
        category_ids = {}
        for category in ("Originais", "Previews", "Entregas"):
            key = f"project:{project.id}:day:{date_segment}.{day_segment}:{category.lower()}"
            category_ids[category.lower()] = self._ensure_folder(
                account, project, key, category, parent_id, access_token, drive_gateway
            )
        return {
            "path": (
                f"Gerenciador de Áudio Visual/{self._safe_name(project.company.name)}/"
                f"{self._safe_name(project.name)}/{date_segment}/{day_segment}"
            ),
            "folders": category_ids,
        }

    @staticmethod
    def _ensure_folder(
        account,
        project,
        folder_key: str,
        name: str,
        parent_id: str,
        access_token: str,
        drive_gateway,
    ) -> str:
        stored = DriveFolderModel.objects.filter(account=account, folder_key=folder_key).first()
        if stored is not None:
            return stored.provider_folder_id
        provider_id = drive_gateway.ensure_folder(access_token, name, parent_id)
        DriveFolderModel.objects.create(
            account=account,
            project=project,
            folder_key=folder_key,
            provider_folder_id=provider_id,
            parent_provider_folder_id=parent_id,
            name=name,
        )
        return provider_id

    @staticmethod
    def _safe_name(value: str) -> str:
        sanitized = " ".join(value.replace("/", "-").replace("\\", "-").split()).strip(". ")
        return sanitized or "Sem nome"

    @staticmethod
    def _digest(raw_state: str) -> str:
        return hashlib.sha256(raw_state.encode("utf-8")).hexdigest()
