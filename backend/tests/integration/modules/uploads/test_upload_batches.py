from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient

from modules.catalog.infrastructure.persistence.models.file_version_model import FileVersionModel
from modules.catalog.infrastructure.persistence.models.media_file_model import MediaFileModel
from modules.companies.infrastructure.persistence.models.company_model import CompanyModel
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel
from modules.drive.infrastructure.google_drive_gateway import ResumableSessionState
from modules.drive.infrastructure.persistence.models import DriveAccountModel, DriveFolderModel
from modules.identity.adapters.api.authenticated_principal import AuthenticatedPrincipal
from modules.identity.infrastructure.cryptography.personal_data_protector import (
    PersonalDataProtector,
)
from modules.identity.infrastructure.persistence.models.user_projection_model import (
    UserProjectionModel,
)
from modules.operations.infrastructure.persistence.models.agent_command_model import (
    AgentCommandModel,
)
from modules.operations.infrastructure.persistence.models.machine_model import MachineModel
from modules.projects.infrastructure.persistence.models.client_model import ClientModel
from modules.projects.infrastructure.persistence.models.project_model import ProjectModel
from modules.uploads.infrastructure.persistence.models import UploadAttemptModel, UploadBatchModel


class FakeOAuthGateway:
    def refresh_access_token(self, refresh_token: str) -> str:
        assert refresh_token == "refresh-token"
        return "access-token"


class FakeResumableDriveGateway:
    def __init__(self) -> None:
        self.created = 0
        self.state = ResumableSessionState("ACTIVE")

    def create_resumable_session(
        self,
        access_token: str,
        parent_id: str,
        name: str,
        size_bytes: int,
        content_type: str,
    ) -> str:
        assert (access_token, parent_id, name, size_bytes) == (
            "access-token",
            "drive-folder",
            "video.mov",
            1000,
        )
        assert content_type == "application/octet-stream"
        self.created += 1
        return f"https://upload.google.test/session-{self.created}"

    def inspect_resumable_session(self, session_url: str, size_bytes: int) -> ResumableSessionState:
        assert session_url.startswith("https://upload.google.test/session-")
        assert size_bytes == 1000
        return self.state

    def get_object(self, access_token: str, object_id: str) -> dict:
        assert access_token == "access-token"
        return {
            "id": object_id,
            "name": "video.mov",
            "size": "1000",
            "sha256Checksum": "a" * 64,
            "mimeType": "video/quicktime",
            "parents": ["drive-folder"],
            "trashed": False,
        }


class UploadBatchTest(TestCase):
    def setUp(self) -> None:
        self.user = UserProjectionModel.objects.create(
            keycloak_subject="upload-owner",
            email_ciphertext=b"encrypted",
            email_lookup_hmac="u" * 64,
        )
        self.company = CompanyModel.objects.create(name="Produtora")
        MembershipModel.objects.create(company=self.company, user=self.user, role="OWNER")
        client = ClientModel.objects.create(
            company=self.company, name="Cliente", normalized_name="cliente"
        )
        self.project = ProjectModel.objects.create(
            company=self.company,
            client=client,
            name="Projeto",
            normalized_name="projeto",
            created_by_user=self.user,
        )
        self.machine = MachineModel.objects.create(
            company_id=self.company.id,
            installation_id="11111111-1111-1111-1111-111111111111",
            registered_by_user_id=self.user.id,
            display_name="Estação",
            os_family="WINDOWS",
            agent_version="0.1.0",
            last_seen_at="2026-08-28T12:00:00Z",
        )
        protector = PersonalDataProtector(
            settings.PERSONAL_DATA_ENCRYPTION_KEYS, settings.PERSONAL_DATA_HMAC_KEY
        )
        self.account = DriveAccountModel.objects.create(
            company=self.company,
            connected_by=self.user,
            provider_account_id="google-account",
            email_ciphertext=protector.encrypt("owner@example.com"),
            refresh_token_ciphertext=protector.encrypt("refresh-token"),
            granted_scopes="drive.file",
            connected_at="2026-08-28T12:00:00Z",
        )
        self.folder = DriveFolderModel.objects.create(
            account=self.account,
            project=self.project,
            folder_key=f"project:{self.project.id}:day:2026.08.28:originais",
            provider_folder_id="drive-folder",
            parent_provider_folder_id="drive-day",
            name="Originais",
        )
        media = MediaFileModel.objects.create(
            company_id=self.company.id,
            project_id=self.project.id,
            created_by_user_id=self.user.id,
            original_name="video.mov",
            display_name="video.mov",
            status="AGUARDANDO_UPLOAD",
        )
        self.version = FileVersionModel.objects.create(
            media_file=media,
            sequence=1,
            size_bytes=1000,
            checksum_algorithm="SHA-256",
            checksum_digest="a" * 64,
        )
        self.api = APIClient()
        self.api.force_authenticate(user=AuthenticatedPrincipal(id=self.user.id))
        self.api.credentials(HTTP_X_COMPANY_ID=str(self.company.id))

    def test_batch_attempt_and_checkpoint_are_idempotent_and_monotonic(self) -> None:
        payload = {
            "project_id": str(self.project.id),
            "machine_id": str(self.machine.id),
            "folder_date": "2026-08-28",
            "idempotency_key": "upload-batch-001",
            "items": [
                {
                    "file_version_id": str(self.version.id),
                    "destination_category": "ORIGINAIS",
                    "final_name": "video.mov",
                }
            ],
        }
        created = self.api.post("/api/v1/upload-batches", payload, format="json")
        repeated = self.api.post("/api/v1/upload-batches", payload, format="json")

        assert created.status_code == 201, created.json()
        assert repeated.status_code == 200
        assert created.json() == repeated.json()
        assert UploadBatchModel.objects.count() == 1
        item_id = created.json()["items"][0]["id"]
        commands = list(AgentCommandModel.objects.all())
        assert len(commands) == 1
        assert commands[0].machine_id == self.machine.id
        assert commands[0].command_type == "UPLOAD_FILE"
        assert commands[0].resource_type == "UPLOAD_ITEM"
        assert str(commands[0].resource_id) == item_id
        assert commands[0].payload == {}

        first_attempt = self.api.post(f"/api/v1/upload-items/{item_id}/attempts")
        repeated_attempt = self.api.post(f"/api/v1/upload-items/{item_id}/attempts")
        assert first_attempt.status_code == 201
        assert repeated_attempt.status_code == 200
        assert first_attempt.json() == repeated_attempt.json()

        attempt_id = first_attempt.json()["id"]
        first_checkpoint = self.api.put(
            f"/api/v1/upload-attempts/{attempt_id}/checkpoint",
            {"confirmed_bytes": 400},
            format="json",
        )
        repeated_checkpoint = self.api.put(
            f"/api/v1/upload-attempts/{attempt_id}/checkpoint",
            {"confirmed_bytes": 400},
            format="json",
        )
        regressive = self.api.put(
            f"/api/v1/upload-attempts/{attempt_id}/checkpoint",
            {"confirmed_bytes": 399},
            format="json",
        )
        assert first_checkpoint.status_code == 200
        assert first_checkpoint.json() == repeated_checkpoint.json()
        assert regressive.status_code == 409

        detail = self.api.get(f"/api/v1/upload-batches/{created.json()['id']}")
        assert detail.status_code == 200
        assert detail.json()["confirmed_bytes"] == 400
        assert detail.json()["progress_percent"] == 40
        assert detail.json()["items"][0]["confirmed_bytes"] == 400
        assert detail.json()["items"][0]["progress_percent"] == 40

        conflicting_payload = {**payload, "folder_date": "2026-08-29"}
        conflict = self.api.post("/api/v1/upload-batches", conflicting_payload, format="json")
        assert conflict.status_code == 409

    def test_realtime_ticket_is_short_lived_and_contains_no_oidc_token(self) -> None:
        response = self.api.post("/api/v1/upload-realtime/ticket")

        assert response.status_code == 201
        assert response.json()["expires_in"] == 60
        assert len(response.json()["ticket"]) >= 40
        assert "token" not in response.json()["ticket"].casefold()

    def test_batch_controls_are_idempotent_and_versioned(self) -> None:
        created = self.api.post(
            "/api/v1/upload-batches",
            {
                "project_id": str(self.project.id),
                "machine_id": str(self.machine.id),
                "folder_date": "2026-08-28",
                "idempotency_key": "control-batch-001",
                "items": [
                    {
                        "file_version_id": str(self.version.id),
                        "destination_category": "ORIGINAIS",
                        "final_name": "video.mov",
                    }
                ],
            },
            format="json",
        ).json()
        endpoint = f"/api/v1/upload-batches/{created['id']}/control"
        pause = {
            "action": "PAUSE",
            "expected_version": created["version"],
            "idempotency_key": "pause-control-001",
        }
        first = self.api.post(endpoint, pause, format="json")
        repeated = self.api.post(endpoint, pause, format="json")
        assert first.status_code == repeated.status_code == 200
        assert first.json() == repeated.json()
        assert first.json()["status"] == "PAUSE_REQUESTED"
        assert first.json()["items"][0]["status"] == "PAUSE_REQUESTED"
        stale = self.api.post(
            endpoint,
            {
                "action": "RESUME",
                "expected_version": created["version"],
                "idempotency_key": "resume-control-001",
            },
            format="json",
        )
        assert stale.status_code == 409

    @patch(
        "modules.uploads.adapters.api.views.create_google_oauth_gateway",
        return_value=FakeOAuthGateway(),
    )
    @patch("modules.uploads.adapters.api.views.create_google_drive_gateway")
    def test_resumable_session_is_encrypted_reused_and_renewed(
        self, drive_factory, _oauth_factory
    ) -> None:
        gateway = FakeResumableDriveGateway()
        drive_factory.return_value = gateway
        created = self.api.post(
            "/api/v1/upload-batches",
            {
                "project_id": str(self.project.id),
                "machine_id": str(self.machine.id),
                "folder_date": "2026-08-28",
                "idempotency_key": "upload-session-001",
                "items": [
                    {
                        "file_version_id": str(self.version.id),
                        "destination_category": "ORIGINAIS",
                        "final_name": "video.mov",
                    }
                ],
            },
            format="json",
        )
        item_id = created.json()["items"][0]["id"]
        endpoint = f"/api/v1/agent/upload-items/{item_id}/session"
        body = {"machine_id": str(self.machine.id)}

        first = self.api.post(endpoint, body, format="json")
        repeated = self.api.post(endpoint, body, format="json")

        assert first.status_code == 201
        assert repeated.status_code == 200
        assert first.json() == repeated.json()
        assert first.json()["media_file_id"] == str(self.version.media_file_id)
        assert first.json()["size_bytes"] == 1000
        assert first.json()["checksum_digest"] == "a" * 64
        assert gateway.created == 1
        attempt = UploadAttemptModel.objects.get(id=first.json()["attempt_id"])
        assert b"upload.google.test" not in bytes(attempt.session_reference_ciphertext)

        gateway.state = ResumableSessionState("ACTIVE", 600)
        reconciled = self.api.post(endpoint, body, format="json")
        assert reconciled.status_code == 200
        assert reconciled.json()["confirmed_bytes"] == 600
        detail = self.api.get(f"/api/v1/upload-batches/{created.json()['id']}")
        assert detail.json()["confirmed_bytes"] == 600

        gateway.state = ResumableSessionState("EXPIRED")
        renewed = self.api.post(endpoint, body, format="json")

        assert renewed.status_code == 201
        assert renewed.json()["sequence"] == 2
        assert renewed.json()["session_url"].endswith("session-2")
        assert gateway.created == 2
        attempt.refresh_from_db()
        assert attempt.status == "EXPIRED"
        assert attempt.failure_code == "SESSION_EXPIRED"

        denied = self.api.post(
            endpoint,
            {"machine_id": "22222222-2222-2222-2222-222222222222"},
            format="json",
        )
        assert denied.status_code == 400

        completion_endpoint = (
            f"/api/v1/agent/upload-attempts/{renewed.json()['attempt_id']}/complete"
        )
        completion_body = {
            "machine_id": str(self.machine.id),
            "provider_object_id": "drive-object-1",
        }
        completed = self.api.post(completion_endpoint, completion_body, format="json")
        repeated_completion = self.api.post(completion_endpoint, completion_body, format="json")
        assert completed.status_code == 201
        assert repeated_completion.status_code == 200
        assert completed.json() == repeated_completion.json()
        assert completed.json()["status"] == "CONFIRMED"
