from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APIClient

from modules.catalog.infrastructure.persistence.models.file_version_model import FileVersionModel
from modules.catalog.infrastructure.persistence.models.media_file_model import MediaFileModel
from modules.companies.infrastructure.persistence.models.company_model import CompanyModel
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel
from modules.identity.adapters.api.authenticated_principal import AuthenticatedPrincipal
from modules.identity.infrastructure.persistence.models.user_projection_model import (
    UserProjectionModel,
)
from modules.operations.infrastructure.persistence.models.machine_model import MachineModel
from modules.projects.infrastructure.persistence.models.client_model import ClientModel
from modules.projects.infrastructure.persistence.models.project_model import ProjectModel


class AgentMediaFileIngestionTest(TestCase):
    def setUp(self) -> None:
        self.user = UserProjectionModel.objects.create(
            keycloak_subject="owner",
            email_ciphertext=b"x",
            email_lookup_hmac="a" * 64,
        )
        self.company = CompanyModel.objects.create(name="Legado")
        MembershipModel.objects.create(
            company=self.company, user=self.user, role="OWNER", status="ACTIVE"
        )
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
            installation_id=uuid4(),
            registered_by_user_id=self.user.id,
            display_name="Estação",
            os_family="WINDOWS",
            agent_version="0.1.0",
            last_seen_at="2026-08-19T12:00:00Z",
        )
        self.api = APIClient()
        self.api.force_authenticate(user=AuthenticatedPrincipal(id=self.user.id))
        self.api.credentials(HTTP_X_COMPANY_ID=str(self.company.id))

    def _payload(self, ingestion_id) -> dict[str, object]:
        return {
            "project_id": str(self.project.id),
            "machine_id": str(self.machine.id),
            "ingestion_id": str(ingestion_id),
            "original_name": r"D:\privado\clip.mov",
            "media_type": "video/quicktime",
            "size_bytes": 4096,
            "checksum_algorithm": "sha256",
            "checksum_digest": "a" * 64,
        }

    def test_repeated_ingestion_returns_same_media_without_local_path(self) -> None:
        ingestion_id = uuid4()

        created = self.api.post(
            "/api/v1/agent/media-files", self._payload(ingestion_id), format="json"
        )
        repeated = self.api.post(
            "/api/v1/agent/media-files", self._payload(ingestion_id), format="json"
        )

        assert created.status_code == 201
        assert repeated.status_code == 200
        assert repeated.json()["id"] == created.json()["id"]
        assert MediaFileModel.objects.count() == 1
        physical = FileVersionModel.objects.get()
        assert physical.ingestion_id == ingestion_id
        assert physical.source_machine_id == self.machine.id
        assert physical.media_file.original_name == "clip.mov"

    def test_reusing_ingestion_id_with_other_content_is_conflict(self) -> None:
        ingestion_id = uuid4()
        self.api.post(
            "/api/v1/agent/media-files", self._payload(ingestion_id), format="json"
        )
        changed = self._payload(ingestion_id)
        changed["checksum_digest"] = "b" * 64

        response = self.api.post("/api/v1/agent/media-files", changed, format="json")

        assert response.status_code == 409
        assert MediaFileModel.objects.count() == 1
