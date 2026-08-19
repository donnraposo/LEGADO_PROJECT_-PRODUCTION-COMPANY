from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.catalog.application.exceptions import TagManagementDeniedError, TagNameConflictError
from modules.catalog.application.use_cases.manage_tags_use_case import (
    CreateCustomTagUseCase,
    ListTagsUseCase,
)
from modules.catalog.infrastructure.persistence.django_tag_repository import DjangoTagRepository
from modules.catalog.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork
from modules.companies.adapters.api.company_context import require_company_membership


class CreateTagRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=80)


class TagCollectionView(APIView):
    def get(self, request) -> Response:
        membership = require_company_membership(request)
        tags = ListTagsUseCase(DjangoTagRepository()).execute(membership.company_id)
        return Response({"items": [self._serialize(tag) for tag in tags]})

    def post(self, request) -> Response:
        membership = require_company_membership(request)
        serializer = CreateTagRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            tag = CreateCustomTagUseCase(DjangoTagRepository(), DjangoUnitOfWork()).execute(
                membership.company_id, membership.role, serializer.validated_data["name"]
            )
        except TagManagementDeniedError as exc:
            raise PermissionDenied("Somente Proprietários podem criar tags.") from exc
        except (TagNameConflictError, ValueError) as exc:
            raise ValidationError("Nome de tag inválido ou já utilizado.") from exc
        return Response(self._serialize(tag), status=status.HTTP_201_CREATED)

    @staticmethod
    def _serialize(tag) -> dict[str, object]:
        return {"id": str(tag.id), "name": tag.name, "is_system": tag.is_system}
