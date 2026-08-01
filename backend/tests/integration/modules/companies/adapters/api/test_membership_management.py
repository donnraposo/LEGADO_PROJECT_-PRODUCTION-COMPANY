from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient

from modules.companies.infrastructure.persistence.models.company_model import CompanyModel
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel
from modules.identity.adapters.api.authenticated_principal import AuthenticatedPrincipal
from modules.identity.domain.value_objects.email_address import EmailAddress
from modules.identity.infrastructure.cryptography.personal_data_protector import (
    PersonalDataProtector,
)
from modules.identity.infrastructure.persistence.models.user_projection_model import (
    UserProjectionModel,
)
from modules.projects.infrastructure.persistence.models.client_model import ClientModel
from modules.projects.infrastructure.persistence.models.project_access_model import (
    ProjectAccessModel,
)
from modules.projects.infrastructure.persistence.models.project_model import ProjectModel


class MembershipManagementTest(TestCase):
    def setUp(self) -> None:
        self.protector = PersonalDataProtector(
            settings.PERSONAL_DATA_ENCRYPTION_KEYS,
            settings.PERSONAL_DATA_HMAC_KEY,
        )
        self.owner = self.create_user("owner", "owner@example.com")
        self.admin = self.create_user("admin", "admin@example.com")
        self.company = CompanyModel.objects.create(name="Legado")
        self.owner_membership = MembershipModel.objects.create(
            company=self.company,
            user=self.owner,
            role="OWNER",
            status="ACTIVE",
        )

    def create_user(self, subject: str, email: str) -> UserProjectionModel:
        normalized = EmailAddress(email).value
        return UserProjectionModel.objects.create(
            keycloak_subject=subject,
            email_ciphertext=self.protector.encrypt(normalized),
            email_lookup_hmac=self.protector.exact_lookup(normalized),
        )

    def api(self, user: UserProjectionModel, with_company: bool = True) -> APIClient:
        client = APIClient()
        client.force_authenticate(user=AuthenticatedPrincipal(id=user.id))
        if with_company:
            client.credentials(HTTP_X_COMPANY_ID=str(self.company.id))
        return client

    def test_invited_user_accepts_once_and_becomes_administrator(self) -> None:
        invitation = self.api(self.owner).post(
            "/api/v1/invitations",
            {"email": "admin@example.com", "role": "ADMINISTRATOR"},
            format="json",
        )
        assert invitation.status_code == 201
        token = invitation.json()["token"]

        accepted = self.api(self.admin, with_company=False).post(
            "/api/v1/invitations/accept",
            {"token": token},
            format="json",
        )

        assert accepted.status_code == 200
        assert accepted.json()["role"] == "ADMINISTRATOR"
        assert (
            self.api(self.admin, with_company=False)
            .post("/api/v1/invitations/accept", {"token": token}, format="json")
            .status_code
            == 400
        )

    def test_invitation_cannot_be_accepted_by_another_email(self) -> None:
        other = self.create_user("other", "other@example.com")
        token = (
            self.api(self.owner)
            .post(
                "/api/v1/invitations",
                {"email": "admin@example.com", "role": "ADMINISTRATOR"},
                format="json",
            )
            .json()["token"]
        )

        response = self.api(other, with_company=False).post(
            "/api/v1/invitations/accept", {"token": token}, format="json"
        )

        assert response.status_code == 400

    def test_last_active_owner_cannot_be_demoted(self) -> None:
        response = self.api(self.owner).patch(
            f"/api/v1/members/{self.owner_membership.id}",
            {"role": "ADMINISTRATOR"},
            format="json",
        )

        assert response.status_code == 400
        self.owner_membership.refresh_from_db()
        assert self.owner_membership.role == "OWNER"

    def test_owner_grants_and_revokes_project_access(self) -> None:
        MembershipModel.objects.create(
            company=self.company,
            user=self.admin,
            role="ADMINISTRATOR",
            status="ACTIVE",
        )
        client = ClientModel.objects.create(
            company=self.company,
            name="Cliente",
            normalized_name="cliente",
        )
        project = ProjectModel.objects.create(
            company=self.company,
            client=client,
            name="Projeto",
            normalized_name="projeto",
            created_by_user=self.owner,
        )
        endpoint = f"/api/v1/projects/{project.id}/access/{self.admin.id}"

        assert self.api(self.owner).put(endpoint).status_code == 204
        assert ProjectAccessModel.objects.filter(project=project, user=self.admin).exists()
        assert self.api(self.owner).delete(endpoint).status_code == 204
        assert not ProjectAccessModel.objects.filter(project=project, user=self.admin).exists()
