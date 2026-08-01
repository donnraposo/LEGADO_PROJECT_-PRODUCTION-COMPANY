from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.company_context import require_company_membership
from modules.companies.domain.value_objects.membership_role import MembershipRole
from modules.projects.adapters.api.serializers.create_project_request_serializer import (
    CreateProjectRequestSerializer,
)
from modules.projects.domain.value_objects.normalized_name import NormalizedName
from modules.projects.infrastructure.persistence.models.client_model import ClientModel
from modules.projects.infrastructure.persistence.models.project_access_model import (
    ProjectAccessModel,
)
from modules.projects.infrastructure.persistence.models.project_model import ProjectModel


class ProjectCollectionView(APIView):
    def get(self, request) -> Response:
        membership = require_company_membership(request)
        projects = ProjectModel.objects.filter(
            company_id=membership.company_id,
            archived_at__isnull=True,
        )
        if membership.role == MembershipRole.ADMINISTRATOR:
            projects = projects.filter(accesses__user_id=request.user.id)
        return Response(
            {"items": [self._serialize(item) for item in projects], "next_cursor": None}
        )

    def post(self, request) -> Response:
        membership = require_company_membership(request)
        serializer = CreateProjectRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = ClientModel.objects.filter(
            id=serializer.validated_data["client_id"],
            company_id=membership.company_id,
            archived_at__isnull=True,
        ).first()
        if client is None:
            raise ValidationError("Cliente não encontrado na empresa ativa.")
        name = NormalizedName(serializer.validated_data["name"])
        try:
            with transaction.atomic():
                project = ProjectModel.objects.create(
                    company_id=membership.company_id,
                    client=client,
                    name=name.value,
                    normalized_name=name.normalized,
                    created_by_user_id=request.user.id,
                )
                if membership.role == MembershipRole.ADMINISTRATOR:
                    ProjectAccessModel.objects.create(project=project, user_id=request.user.id)
        except IntegrityError as exc:
            raise ValidationError("Já existe um projeto com este nome para o cliente.") from exc
        return Response(self._serialize(project), status=status.HTTP_201_CREATED)

    @staticmethod
    def _serialize(project: ProjectModel) -> dict[str, object]:
        return {
            "id": str(project.id),
            "client_id": str(project.client_id),
            "name": project.name,
            "version": project.version,
        }
