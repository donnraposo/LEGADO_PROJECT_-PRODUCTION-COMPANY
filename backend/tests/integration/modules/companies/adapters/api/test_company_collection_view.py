from django.test import TestCase
from rest_framework.test import APIClient

from modules.companies.infrastructure.persistence.models.company_model import CompanyModel
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel
from modules.identity.adapters.api.authenticated_principal import AuthenticatedPrincipal
from modules.identity.infrastructure.persistence.models.user_projection_model import (
    UserProjectionModel,
)


class CompanyCollectionViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserProjectionModel.objects.create(
            keycloak_subject="keycloak-user-1",
            email_ciphertext=b"encrypted",
            email_lookup_hmac="a" * 64,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=AuthenticatedPrincipal(id=self.user.id))

    def test_creator_becomes_owner_and_can_list_company(self) -> None:
        response = self.client.post(
            "/api/v1/companies",
            {"name": "  Produtora   Legado  "},
            format="json",
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Produtora Legado"
        assert response.json()["role"] == "OWNER"
        assert CompanyModel.objects.count() == 1
        assert MembershipModel.objects.filter(
            company_id=response.json()["id"],
            user=self.user,
            role="OWNER",
            status="ACTIVE",
        ).exists()

        listing = self.client.get("/api/v1/companies")
        assert listing.status_code == 200
        assert listing.json()["items"] == [response.json()]
        assert listing.json()["next_cursor"] is None

    def test_unauthenticated_request_uses_problem_json(self) -> None:
        client = APIClient()

        response = client.get("/api/v1/companies")

        assert response.status_code == 403
        assert response["Content-Type"] == "application/problem+json"
        assert response.json()["code"] == "AUTHENTICATION_REQUIRED"
