from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.company_context import require_company_membership
from modules.projects.adapters.api.serializers.create_client_request_serializer import (
    CreateClientRequestSerializer,
)
from modules.projects.application.dto.client_summary import ClientSummary
from modules.projects.application.dto.create_client_command import CreateClientCommand
from modules.projects.application.exceptions import ClientNameConflictError
from modules.projects.application.use_cases.create_client_use_case import CreateClientUseCase
from modules.projects.application.use_cases.list_clients_use_case import ListClientsUseCase
from modules.projects.infrastructure.persistence.django_client_repository import (
    DjangoClientRepository,
)
from modules.projects.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork


class ClientCollectionView(APIView):
    def get(self, request) -> Response:
        membership = require_company_membership(request)
        clients = ListClientsUseCase(DjangoClientRepository()).execute(membership.company_id)
        return Response({"items": [self._serialize(item) for item in clients], "next_cursor": None})

    def post(self, request) -> Response:
        membership = require_company_membership(request)
        serializer = CreateClientRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            client = CreateClientUseCase(DjangoClientRepository(), DjangoUnitOfWork()).execute(
                CreateClientCommand(membership.company_id, serializer.validated_data["name"])
            )
        except ClientNameConflictError as exc:
            raise ValidationError("Já existe um cliente com este nome na empresa.") from exc
        return Response(self._serialize(client), status=status.HTTP_201_CREATED)

    @staticmethod
    def _serialize(client: ClientSummary) -> dict[str, object]:
        return {"id": str(client.id), "name": client.name, "version": client.version}
