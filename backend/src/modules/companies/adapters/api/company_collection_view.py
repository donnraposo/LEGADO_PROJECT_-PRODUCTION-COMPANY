from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.serializers.create_company_request_serializer import (
    CreateCompanyRequestSerializer,
)
from modules.companies.application.dto.company_membership_summary import (
    CompanyMembershipSummary,
)
from modules.companies.application.dto.create_company_command import CreateCompanyCommand
from modules.companies.application.use_cases.create_company_use_case import (
    CreateCompanyUseCase,
)
from modules.companies.application.use_cases.list_user_companies_use_case import (
    ListUserCompaniesUseCase,
)
from modules.companies.infrastructure.persistence.django_company_repository import (
    DjangoCompanyRepository,
)
from modules.companies.infrastructure.persistence.django_membership_repository import (
    DjangoMembershipRepository,
)
from modules.companies.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork


class CompanyCollectionView(APIView):
    @staticmethod
    def _serialize(summary: CompanyMembershipSummary) -> dict[str, object]:
        return {
            "id": str(summary.company_id),
            "name": summary.name,
            "role": summary.role,
            "version": summary.version,
        }

    def get(self, request) -> Response:
        companies = ListUserCompaniesUseCase(DjangoCompanyRepository()).execute(
            request.user.id
        )
        return Response(
            {"items": [self._serialize(company) for company in companies], "next_cursor": None}
        )

    def post(self, request) -> Response:
        serializer = CreateCompanyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = CreateCompanyUseCase(
            DjangoCompanyRepository(),
            DjangoMembershipRepository(),
            DjangoUnitOfWork(),
        ).execute(
            CreateCompanyCommand(
                actor_user_id=request.user.id,
                name=serializer.validated_data["name"],
            )
        )
        return Response(self._serialize(company), status=status.HTTP_201_CREATED)
