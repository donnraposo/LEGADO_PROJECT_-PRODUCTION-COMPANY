from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.company_context import require_company_membership
from modules.projects.adapters.api.serializers.create_project_request_serializer import (
    CreateProjectRequestSerializer,
)
from modules.projects.application.dto.create_project_command import CreateProjectCommand
from modules.projects.application.dto.project_summary import ProjectSummary
from modules.projects.application.exceptions import ClientNotFoundError, ProjectNameConflictError
from modules.projects.application.use_cases.create_project_use_case import CreateProjectUseCase
from modules.projects.application.use_cases.list_projects_use_case import ListProjectsUseCase
from modules.projects.infrastructure.persistence.django_project_repository import (
    DjangoProjectRepository,
)
from modules.projects.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork


class ProjectCollectionView(APIView):
    def get(self, request) -> Response:
        membership = require_company_membership(request)
        projects = ListProjectsUseCase(DjangoProjectRepository()).execute(
            membership.company_id, request.user.id, membership.role
        )
        return Response(
            {"items": [self._serialize(item) for item in projects], "next_cursor": None}
        )

    def post(self, request) -> Response:
        membership = require_company_membership(request)
        serializer = CreateProjectRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            project = CreateProjectUseCase(DjangoProjectRepository(), DjangoUnitOfWork()).execute(
                CreateProjectCommand(
                    membership.company_id,
                    serializer.validated_data["client_id"],
                    request.user.id,
                    membership.role,
                    serializer.validated_data["name"],
                )
            )
        except ClientNotFoundError as exc:
            raise ValidationError("Cliente não encontrado na empresa ativa.") from exc
        except ProjectNameConflictError as exc:
            raise ValidationError("Já existe um projeto com este nome para o cliente.") from exc
        return Response(self._serialize(project), status=status.HTTP_201_CREATED)

    @staticmethod
    def _serialize(project: ProjectSummary) -> dict[str, object]:
        return {
            "id": str(project.id),
            "client_id": str(project.client_id),
            "name": project.name,
            "version": project.version,
        }
