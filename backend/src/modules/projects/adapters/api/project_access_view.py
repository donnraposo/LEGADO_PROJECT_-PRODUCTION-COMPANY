from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.company_context import require_owner
from modules.companies.domain.value_objects.membership_role import MembershipRole
from modules.companies.domain.value_objects.membership_status import MembershipStatus
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel
from modules.projects.infrastructure.persistence.models.project_access_model import (
    ProjectAccessModel,
)
from modules.projects.infrastructure.persistence.models.project_model import ProjectModel


class ProjectAccessView(APIView):
    def put(self, request, project_id, user_id) -> Response:
        owner = require_owner(request)
        project = self._project(project_id, owner.company_id)
        member = MembershipModel.objects.filter(
            company_id=owner.company_id,
            user_id=user_id,
            role=MembershipRole.ADMINISTRATOR,
            status=MembershipStatus.ACTIVE,
        ).first()
        if member is None:
            raise ValidationError("O usuário não é Administrador ativo da empresa.")
        ProjectAccessModel.objects.get_or_create(project=project, user_id=user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, project_id, user_id) -> Response:
        owner = require_owner(request)
        project = self._project(project_id, owner.company_id)
        ProjectAccessModel.objects.filter(project=project, user_id=user_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _project(project_id, company_id) -> ProjectModel:
        project = ProjectModel.objects.filter(
            id=project_id,
            company_id=company_id,
            archived_at__isnull=True,
        ).first()
        if project is None:
            raise NotFound("Projeto não encontrado.")
        return project
