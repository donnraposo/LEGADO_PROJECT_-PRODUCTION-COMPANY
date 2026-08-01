from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.projects.adapters.api.company_context import require_company_membership
from modules.projects.adapters.api.serializers.create_client_request_serializer import (
    CreateClientRequestSerializer,
)
from modules.projects.domain.value_objects.normalized_name import NormalizedName
from modules.projects.infrastructure.persistence.models.client_model import ClientModel


class ClientCollectionView(APIView):
    def get(self, request) -> Response:
        membership = require_company_membership(request)
        clients = ClientModel.objects.filter(
            company_id=membership.company_id,
            archived_at__isnull=True,
        )
        return Response({"items": [self._serialize(item) for item in clients], "next_cursor": None})

    def post(self, request) -> Response:
        membership = require_company_membership(request)
        serializer = CreateClientRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name = NormalizedName(serializer.validated_data["name"])
        try:
            client = ClientModel.objects.create(
                company_id=membership.company_id,
                name=name.value,
                normalized_name=name.normalized,
            )
        except IntegrityError as exc:
            raise ValidationError("Já existe um cliente com este nome na empresa.") from exc
        return Response(self._serialize(client), status=status.HTTP_201_CREATED)

    @staticmethod
    def _serialize(client: ClientModel) -> dict[str, object]:
        return {"id": str(client.id), "name": client.name, "version": client.version}
