import uuid

from django.test import TestCase
from rest_framework.test import APIClient

from modules.companies.infrastructure.persistence.models.company_model import CompanyModel
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel
from modules.identity.adapters.api.authenticated_principal import AuthenticatedPrincipal
from modules.identity.infrastructure.persistence.models.user_projection_model import (
    UserProjectionModel,
)
from modules.operations.infrastructure.persistence.models.agent_command_model import (
    AgentCommandModel,
)
from modules.operations.infrastructure.persistence.models.machine_model import MachineModel


class AgentOperationsTest(TestCase):
    def setUp(self) -> None:
        self.user = UserProjectionModel.objects.create(
            keycloak_subject="operations-user",
            email_ciphertext=b"x",
            email_lookup_hmac="e" * 64,
        )
        self.company = CompanyModel.objects.create(name="Legado")
        MembershipModel.objects.create(
            company=self.company, user=self.user, role="OWNER", status="ACTIVE"
        )
        self.api = APIClient()
        self.api.force_authenticate(user=AuthenticatedPrincipal(id=self.user.id))
        self.api.credentials(HTTP_X_COMPANY_ID=str(self.company.id))
        self.installation_id = uuid.uuid4()

    def _heartbeat(self):
        return self.api.post(
            "/api/v1/agent/machines/heartbeat",
            {
                "installation_id": str(self.installation_id),
                "display_name": "Estação 01",
                "os_family": "WINDOWS",
                "agent_version": "0.1.0",
            },
            format="json",
        )

    @staticmethod
    def _command_payload(machine_id, idempotency_key="reconcile-file-0001"):
        return {
            "machine_id": machine_id,
            "command_type": "RECONCILE_MEDIA_FILE",
            "resource_type": "MEDIA_FILE",
            "resource_id": str(uuid.uuid4()),
            "payload": {"verification": "IDENTITY_AND_CHECKSUM"},
            "idempotency_key": idempotency_key,
        }

    def test_heartbeat_is_idempotent_for_company_and_installation(self) -> None:
        first = self._heartbeat()
        second = self._heartbeat()

        assert first.status_code == 200
        assert second.status_code == 200
        assert first.json()["id"] == second.json()["id"]
        assert MachineModel.objects.count() == 1

    def test_command_creation_is_idempotent_and_sequenced(self) -> None:
        machine_id = self._heartbeat().json()["id"]
        payload = self._command_payload(machine_id)

        created = self.api.post("/api/v1/agent/commands", payload, format="json")
        repeated = self.api.post("/api/v1/agent/commands", payload, format="json")
        another = self.api.post(
            "/api/v1/agent/commands",
            self._command_payload(machine_id, "reconcile-file-0002"),
            format="json",
        )
        listed = self.api.get(f"/api/v1/agent/machines/{machine_id}/commands")

        assert created.status_code == 201
        assert repeated.status_code == 200
        assert repeated.json()["id"] == created.json()["id"]
        assert another.json()["sequence"] == 2
        assert [item["sequence"] for item in listed.json()["items"]] == [1, 2]
        assert AgentCommandModel.objects.count() == 2

    def test_reused_key_with_other_content_conflicts(self) -> None:
        machine_id = self._heartbeat().json()["id"]
        first = self._command_payload(machine_id)
        changed = {**first, "payload": {"verification": "OTHER"}}

        self.api.post("/api/v1/agent/commands", first, format="json")
        conflict = self.api.post("/api/v1/agent/commands", changed, format="json")

        assert conflict.status_code == 409

    def test_sensitive_payload_is_rejected(self) -> None:
        machine_id = self._heartbeat().json()["id"]
        payload = self._command_payload(machine_id)
        payload["payload"] = {"nested": {"access_token": "never-store"}}

        response = self.api.post("/api/v1/agent/commands", payload, format="json")

        assert response.status_code == 400
        assert AgentCommandModel.objects.count() == 0

    def test_other_company_cannot_access_machine(self) -> None:
        machine_id = self._heartbeat().json()["id"]
        other = CompanyModel.objects.create(name="Outra")
        MembershipModel.objects.create(
            company=other, user=self.user, role="OWNER", status="ACTIVE"
        )
        self.api.credentials(HTTP_X_COMPANY_ID=str(other.id))

        listed = self.api.get(f"/api/v1/agent/machines/{machine_id}/commands")
        created = self.api.post(
            "/api/v1/agent/commands", self._command_payload(machine_id), format="json"
        )

        assert listed.status_code == 404
        assert created.status_code == 404

    def test_agent_reports_progress_without_state_regression(self) -> None:
        machine_id = self._heartbeat().json()["id"]
        command = self.api.post(
            "/api/v1/agent/commands",
            self._command_payload(machine_id),
            format="json",
        ).json()
        endpoint = f"/api/v1/agent/commands/{command['id']}"

        acknowledged = self.api.patch(
            endpoint,
            {
                "machine_id": machine_id,
                "expected_version": 1,
                "status": "ACKNOWLEDGED",
            },
            format="json",
        )
        running = self.api.patch(
            endpoint,
            {
                "machine_id": machine_id,
                "expected_version": 2,
                "status": "RUNNING",
                "progress_percent": 35,
            },
            format="json",
        )
        stale = self.api.patch(
            endpoint,
            {
                "machine_id": machine_id,
                "expected_version": 2,
                "status": "SUCCEEDED",
            },
            format="json",
        )
        regressed_progress = self.api.patch(
            endpoint,
            {
                "machine_id": machine_id,
                "expected_version": 3,
                "status": "RUNNING",
                "progress_percent": 20,
            },
            format="json",
        )
        completed = self.api.patch(
            endpoint,
            {
                "machine_id": machine_id,
                "expected_version": 3,
                "status": "SUCCEEDED",
                "result": {"verified": True},
            },
            format="json",
        )
        regressed = self.api.patch(
            endpoint,
            {
                "machine_id": machine_id,
                "expected_version": 4,
                "status": "RUNNING",
            },
            format="json",
        )

        assert acknowledged.json()["status"] == "ACKNOWLEDGED"
        assert running.json()["progress_percent"] == 35
        assert stale.status_code == 409
        assert regressed_progress.status_code == 400
        assert completed.json()["progress_percent"] == 100
        assert completed.json()["result"] == {"verified": True}
        assert regressed.status_code == 400
