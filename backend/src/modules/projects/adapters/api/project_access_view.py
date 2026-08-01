from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from config.infrastructure.django_company_member_authorization import (
    DjangoCompanyMemberAuthorization,
)
from modules.companies.adapters.api.company_context import require_owner
from modules.projects.application.dto.change_project_access_command import (
    ChangeProjectAccessCommand,
)
from modules.projects.application.exceptions import (
    ActiveAdministratorRequiredError,
    ProjectNotFoundError,
)
from modules.projects.application.use_cases.grant_project_access_use_case import (
    GrantProjectAccessUseCase,
)
from modules.projects.application.use_cases.revoke_project_access_use_case import (
    RevokeProjectAccessUseCase,
)
from modules.projects.infrastructure.audit.django_project_access_audit import (
    DjangoProjectAccessAudit,
)
from modules.projects.infrastructure.persistence.django_project_access_repository import (
    DjangoProjectAccessRepository,
)
from modules.projects.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork


class ProjectAccessView(APIView):
    def put(self, request, project_id, user_id) -> Response:
        owner = require_owner(request)
        command = self._command(request, owner.company_id, project_id, user_id)
        try:
            GrantProjectAccessUseCase(
                DjangoProjectAccessRepository(),
                DjangoCompanyMemberAuthorization(),
                DjangoProjectAccessAudit(),
                DjangoUnitOfWork(),
            ).execute(command)
        except ProjectNotFoundError as exc:
            raise NotFound("Projeto não encontrado.") from exc
        except ActiveAdministratorRequiredError as exc:
            raise ValidationError("O usuário não é Administrador ativo da empresa.") from exc
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, project_id, user_id) -> Response:
        owner = require_owner(request)
        command = self._command(request, owner.company_id, project_id, user_id)
        try:
            RevokeProjectAccessUseCase(
                DjangoProjectAccessRepository(),
                DjangoProjectAccessAudit(),
                DjangoUnitOfWork(),
            ).execute(command)
        except ProjectNotFoundError as exc:
            raise NotFound("Projeto não encontrado.") from exc
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _command(request, company_id, project_id, user_id) -> ChangeProjectAccessCommand:
        return ChangeProjectAccessCommand(
            company_id=company_id,
            actor_user_id=request.user.id,
            project_id=project_id,
            administrator_user_id=user_id,
        )
