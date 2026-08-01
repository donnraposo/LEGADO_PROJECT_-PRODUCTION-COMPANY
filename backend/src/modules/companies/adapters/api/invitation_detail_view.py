from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.company_context import require_owner
from modules.companies.application.dto.cancel_invitation_command import (
    CancelInvitationCommand,
)
from modules.companies.application.exceptions import PendingInvitationNotFoundError
from modules.companies.application.use_cases.cancel_invitation_use_case import (
    CancelInvitationUseCase,
)
from modules.companies.infrastructure.audit.django_audit_event_recorder import (
    DjangoAuditEventRecorder,
)
from modules.companies.infrastructure.persistence.django_invitation_cancellation_repository import (
    DjangoInvitationCancellationRepository,
)
from modules.companies.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork


class InvitationDetailView(APIView):
    def delete(self, request, invitation_id) -> Response:
        membership = require_owner(request)
        try:
            CancelInvitationUseCase(
                DjangoInvitationCancellationRepository(),
                DjangoAuditEventRecorder(),
                DjangoUnitOfWork(),
            ).execute(
                CancelInvitationCommand(
                    company_id=membership.company_id,
                    actor_user_id=request.user.id,
                    invitation_id=invitation_id,
                    cancelled_at=timezone.now(),
                )
            )
        except PendingInvitationNotFoundError as exc:
            raise NotFound("Convite pendente não encontrado.") from exc
        return Response(status=status.HTTP_204_NO_CONTENT)
