import hashlib
import secrets
from datetime import timedelta
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from modules.drive.application.exceptions import InvalidOAuthStateError
from modules.drive.infrastructure.google_oauth_gateway import GoogleCredentials
from modules.drive.infrastructure.persistence.models import (
    DriveAccountModel,
    DriveOAuthStateModel,
)
from modules.identity.infrastructure.cryptography.personal_data_protector import (
    PersonalDataProtector,
)


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
        DriveAccountModel.objects.update_or_create(
            company_id=state.company_id,
            defaults={
                "connected_by_id": state.actor_user_id,
                "provider_account_id": credentials.provider_account_id,
                "email_ciphertext": self._protector.encrypt(credentials.email),
                "refresh_token_ciphertext": self._protector.encrypt(credentials.refresh_token),
                "granted_scopes": credentials.granted_scopes,
                "connected_at": now,
                "disconnected_at": None,
            },
        )

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

    @staticmethod
    def _digest(raw_state: str) -> str:
        return hashlib.sha256(raw_state.encode("utf-8")).hexdigest()
