from django.test import TestCase
from rest_framework.test import APIClient

from modules.companies.infrastructure.persistence.models.company_model import CompanyModel
from modules.companies.infrastructure.persistence.models.membership_model import (
    MembershipModel,
)
from modules.identity.adapters.api.authenticated_principal import AuthenticatedPrincipal
from modules.identity.infrastructure.persistence.models.user_projection_model import (
    UserProjectionModel,
)
from modules.projects.infrastructure.persistence.models.project_access_model import (
    ProjectAccessModel,
)


class ProjectCollectionsTest(TestCase):
    def setUp(self) -> None:
        self.owner = self.create_user("owner", "a")
        self.admin = self.create_user("admin", "b")
        self.outsider = self.create_user("outsider", "c")
        self.company = CompanyModel.objects.create(name="Legado")
        MembershipModel.objects.create(
            company=self.company, user=self.owner, role="OWNER", status="ACTIVE"
        )
        MembershipModel.objects.create(
            company=self.company,
            user=self.admin,
            role="ADMINISTRATOR",
            status="ACTIVE",
        )

    @staticmethod
    def create_user(subject: str, hmac_prefix: str) -> UserProjectionModel:
        return UserProjectionModel.objects.create(
            keycloak_subject=subject,
            email_ciphertext=b"x",
            email_lookup_hmac=hmac_prefix * 64,
        )

    def client_for(self, user: UserProjectionModel) -> APIClient:
        client = APIClient()
        client.force_authenticate(user=AuthenticatedPrincipal(id=user.id))
        client.credentials(HTTP_X_COMPANY_ID=str(self.company.id))
        return client

    def test_owner_creates_client_and_project(self) -> None:
        client = self.client_for(self.owner)
        created_client = client.post("/api/v1/clients", {"name": "  Cliente   A "}, format="json")
        assert created_client.status_code == 201
        project = client.post(
            "/api/v1/projects",
            {"client_id": created_client.json()["id"], "name": " Filme "},
            format="json",
        )
        assert project.status_code == 201
        assert client.get("/api/v1/projects").json()["items"] == [project.json()]

    def test_administrator_gets_access_to_project_created_by_them(self) -> None:
        owner_client = self.client_for(self.owner)
        client_id = owner_client.post("/api/v1/clients", {"name": "Cliente"}, format="json").json()[
            "id"
        ]
        admin_client = self.client_for(self.admin)
        project = admin_client.post(
            "/api/v1/projects",
            {"client_id": client_id, "name": "Projeto"},
            format="json",
        )
        assert project.status_code == 201
        assert ProjectAccessModel.objects.filter(
            project_id=project.json()["id"], user=self.admin
        ).exists()
        assert admin_client.get("/api/v1/projects").json()["items"] == [project.json()]

    def test_user_outside_company_is_denied(self) -> None:
        response = self.client_for(self.outsider).get("/api/v1/clients")
        assert response.status_code == 403

    def test_client_from_another_company_cannot_be_used(self) -> None:
        other_company = CompanyModel.objects.create(name="Outra")
        MembershipModel.objects.create(
            company=other_company, user=self.owner, role="OWNER", status="ACTIVE"
        )
        client = self.client_for(self.owner)
        other_client = APIClient()
        other_client.force_authenticate(user=AuthenticatedPrincipal(id=self.owner.id))
        other_client.credentials(HTTP_X_COMPANY_ID=str(other_company.id))
        foreign_client_id = other_client.post(
            "/api/v1/clients", {"name": "Externo"}, format="json"
        ).json()["id"]
        response = client.post(
            "/api/v1/projects",
            {"client_id": foreign_client_id, "name": "Inválido"},
            format="json",
        )
        assert response.status_code == 400
