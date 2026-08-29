from unittest.mock import patch

from django.conf import settings
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from modules.companies.infrastructure.persistence.models.company_model import CompanyModel
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel
from modules.drive.infrastructure.django_drive_service import DjangoDriveService
from modules.drive.infrastructure.google_oauth_gateway import GoogleCredentials
from modules.drive.infrastructure.persistence.models import DriveAccountModel, DriveFolderModel
from modules.identity.adapters.api.authenticated_principal import AuthenticatedPrincipal
from modules.identity.infrastructure.cryptography.personal_data_protector import (
    PersonalDataProtector,
)
from modules.identity.infrastructure.persistence.models.user_projection_model import (
    UserProjectionModel,
)
from modules.projects.infrastructure.persistence.models.client_model import ClientModel
from modules.projects.infrastructure.persistence.models.project_model import ProjectModel


class FakeGateway:
    def authorization_url(self, state: str) -> str:
        return f"https://accounts.google.test/authorize?state={state}"

    def exchange_code(self, code: str) -> GoogleCredentials:
        assert code == "google-code"
        return GoogleCredentials(
            "google-user", "owner@gmail.com", "raw-refresh-token", "drive.file"
        )

    def refresh_access_token(self, refresh_token: str) -> str:
        assert refresh_token == "raw-refresh-token"
        return "temporary-access-token"


class FakeDriveGateway:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def ensure_folder(self, access_token: str, name: str, parent_id: str = "") -> str:
        assert access_token == "temporary-access-token"
        self.calls.append((name, parent_id))
        return f"folder-{len(self.calls)}"


@override_settings(
    GOOGLE_OAUTH_CLIENT_ID="client-id",
    GOOGLE_OAUTH_CLIENT_SECRET="client-secret",
    GOOGLE_OAUTH_FRONTEND_RETURN_URL="http://127.0.0.1:5173/",
)
class DriveOAuthTest(TestCase):
    def setUp(self) -> None:
        self.user = UserProjectionModel.objects.create(
            keycloak_subject="owner",
            email_ciphertext=b"encrypted",
            email_lookup_hmac="d" * 64,
        )
        self.company = CompanyModel.objects.create(name="Legado")
        MembershipModel.objects.create(company=self.company, user=self.user, role="OWNER")
        self.client = APIClient()
        self.client.force_authenticate(user=AuthenticatedPrincipal(id=self.user.id))
        self.client.credentials(HTTP_X_COMPANY_ID=str(self.company.id))

    @patch(
        "modules.drive.adapters.api.views.create_google_oauth_gateway",
        return_value=FakeGateway(),
    )
    def test_authorization_and_callback_store_only_encrypted_refresh_token(self, _gateway) -> None:
        authorization = self.client.post("/api/v1/drive/oauth/authorization")

        assert authorization.status_code == 200
        state = authorization.json()["authorization_url"].split("state=", 1)[1]
        callback = APIClient().get(
            "/api/v1/drive/oauth/callback",
            {"code": "google-code", "state": state},
        )

        assert callback.status_code == 302
        assert callback.url == "http://127.0.0.1:5173/?drive=connected"
        account = DriveAccountModel.objects.get(company=self.company)
        assert b"raw-refresh-token" not in bytes(account.refresh_token_ciphertext)
        protector = PersonalDataProtector(
            settings.PERSONAL_DATA_ENCRYPTION_KEYS,
            settings.PERSONAL_DATA_HMAC_KEY,
        )
        assert protector.decrypt(bytes(account.refresh_token_ciphertext)) == "raw-refresh-token"

        status_response = self.client.get("/api/v1/drive/account")
        assert status_response.json() == {
            "connected": True,
            "account_email": "owner@gmail.com",
            "connected_at": account.connected_at.isoformat(),
        }
        assert "token" not in str(status_response.json()).lower()

        assert self.client.delete("/api/v1/drive/account").status_code == 204
        account.refresh_from_db()
        assert bytes(account.refresh_token_ciphertext) == b""
        assert bytes(account.email_ciphertext) == b""

    def test_oauth_state_can_only_be_consumed_once(self) -> None:
        service = DjangoDriveService(
            PersonalDataProtector(
                settings.PERSONAL_DATA_ENCRYPTION_KEYS,
                settings.PERSONAL_DATA_HMAC_KEY,
            )
        )
        state = service.create_state(self.company.id, self.user.id)
        service.consume_state(state)

        with self.assertRaisesMessage(ValueError, "Autorização expirada ou já utilizada"):
            service.consume_state(state)

    def test_non_owner_cannot_start_or_disconnect_connection(self) -> None:
        second_user = UserProjectionModel.objects.create(
            keycloak_subject="administrator",
            email_ciphertext=b"encrypted",
            email_lookup_hmac="e" * 64,
        )
        MembershipModel.objects.create(
            company=self.company,
            user=second_user,
            role="ADMINISTRATOR",
        )
        client = APIClient()
        client.force_authenticate(user=AuthenticatedPrincipal(id=second_user.id))
        client.credentials(HTTP_X_COMPANY_ID=str(self.company.id))

        assert client.post("/api/v1/drive/oauth/authorization").status_code == 403
        assert client.delete("/api/v1/drive/account").status_code == 403

    @patch(
        "modules.drive.adapters.api.views.create_google_drive_gateway",
    )
    @patch(
        "modules.drive.adapters.api.views.create_google_oauth_gateway",
        return_value=FakeGateway(),
    )
    def test_owner_prepares_idempotent_daily_folder_tree(self, _oauth, drive_factory) -> None:
        self.client.post("/api/v1/drive/oauth/authorization")
        service = DjangoDriveService(
            PersonalDataProtector(
                settings.PERSONAL_DATA_ENCRYPTION_KEYS,
                settings.PERSONAL_DATA_HMAC_KEY,
            )
        )
        state = service.create_state(self.company.id, self.user.id)
        service.connect(service.consume_state(state), FakeGateway().exchange_code("google-code"))
        client_record = ClientModel.objects.create(
            company=self.company,
            name="Cliente",
            normalized_name="cliente",
        )
        project = ProjectModel.objects.create(
            company=self.company,
            client=client_record,
            name="Campanha",
            normalized_name="campanha",
            created_by_user=self.user,
        )
        drive_gateway = FakeDriveGateway()
        drive_factory.return_value = drive_gateway

        first = self.client.post(
            "/api/v1/drive/folders/ensure",
            {"project_id": str(project.id), "date": "2026-08-25"},
            format="json",
        )
        second = self.client.post(
            "/api/v1/drive/folders/ensure",
            {"project_id": str(project.id), "date": "2026-08-25"},
            format="json",
        )

        assert first.status_code == 200
        assert second.status_code == 200
        assert first.json()["path"] == (
            "Gerenciador de Áudio Visual/Legado/Campanha/2026.08/25"
        )
        assert first.json() == second.json()
        assert [name for name, _parent in drive_gateway.calls] == [
            "Gerenciador de Áudio Visual",
            "Legado",
            "Campanha",
            "2026.08",
            "25",
            "Originais",
            "Previews",
            "Entregas",
        ]
        assert DriveFolderModel.objects.count() == 8
