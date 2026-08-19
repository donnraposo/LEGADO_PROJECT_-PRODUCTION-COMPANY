from django.test import TestCase
from rest_framework.test import APIClient

from modules.audit.infrastructure.persistence.models.audit_event_model import AuditEventModel
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


class MediaFileReconciliationTest(TestCase):
    def setUp(self) -> None:
        self.user = UserProjectionModel.objects.create(
            keycloak_subject="owner",
            email_ciphertext=b"x",
            email_lookup_hmac="a" * 64,
        )
        self.company = CompanyModel.objects.create(name="Legado")
        MembershipModel.objects.create(
            company=self.company,
            user=self.user,
            role="OWNER",
            status="ACTIVE",
        )
        client = ClientModel.objects.create(
            company=self.company,
            name="Cliente",
            normalized_name="cliente",
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
            installation_id="00000000-0000-0000-0000-000000000001",
            registered_by_user_id=self.user.id,
            display_name="Estação",
            os_family="WINDOWS",
            agent_version="0.1.0",
            last_seen_at="2026-08-18T20:00:00Z",
        )
        self.media = MediaFileModel.objects.create(
            company_id=self.company.id,
            project_id=self.project.id,
            created_by_user_id=self.user.id,
            original_name="clip.mov",
            display_name="clip.mov",
        )
        FileVersionModel.objects.create(
            media_file=self.media,
            sequence=1,
            size_bytes=100,
            checksum_algorithm="sha256",
            checksum_digest="a" * 64,
        )
        self.api = APIClient()
        self.api.force_authenticate(user=AuthenticatedPrincipal(id=self.user.id))
        self.api.credentials(HTTP_X_COMPANY_ID=str(self.company.id))
        self.endpoint = f"/api/v1/agent/media-files/{self.media.id}/state"

    def _patch(self, status: str, expected_version: int = 1, machine_id=None):
        return self.api.patch(
            self.endpoint,
            {
                "machine_id": str(machine_id or self.machine.id),
                "expected_version": expected_version,
                "status": status,
            },
            format="json",
        )

    def test_reconciles_valid_transition_and_audits_machine(self) -> None:
        response = self._patch("ANALISADO")

        assert response.status_code == 200
        assert response.json()["status"] == "ANALISADO"
        assert response.json()["version"] == 2
        assert FileVersionModel.objects.get().source_machine_id == self.machine.id
        event = AuditEventModel.objects.get(event_type="MEDIA_FILE_STATE_RECONCILED")
        assert event.old_state == {
            "status": "DESCOBERTO",
            "machine_id": str(self.machine.id),
        }
        assert event.new_state == {
            "status": "ANALISADO",
            "machine_id": str(self.machine.id),
        }

    def test_repeating_same_state_is_idempotent(self) -> None:
        first = self._patch("ANALISADO")
        repeated = self._patch("ANALISADO", expected_version=1)

        assert first.status_code == 200
        assert repeated.status_code == 200
        assert repeated.json()["version"] == 2
        assert AuditEventModel.objects.filter(
            event_type="MEDIA_FILE_STATE_RECONCILED"
        ).count() == 1

    def test_rejects_invalid_transition_and_stale_version(self) -> None:
        invalid = self._patch("SINCRONIZADO")
        first = self._patch("ANALISADO")
        stale = self._patch("AGUARDANDO_CONFIRMACAO", expected_version=1)

        assert invalid.status_code == 400
        assert first.status_code == 200
        assert stale.status_code == 409

    def test_rejects_machine_from_another_company(self) -> None:
        foreign_company = CompanyModel.objects.create(name="Outra")
        foreign_machine = MachineModel.objects.create(
            company_id=foreign_company.id,
            installation_id="00000000-0000-0000-0000-000000000002",
            registered_by_user_id=self.user.id,
            display_name="Outra estação",
            os_family="WINDOWS",
            agent_version="0.1.0",
            last_seen_at="2026-08-18T20:00:00Z",
        )

        response = self._patch("ANALISADO", machine_id=foreign_machine.id)

        assert response.status_code == 404
        self.media.refresh_from_db()
        assert self.media.status == "DESCOBERTO"
