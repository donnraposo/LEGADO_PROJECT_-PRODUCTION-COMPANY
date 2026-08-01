from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.serializers.accept_invitation_request_serializer import (
    AcceptInvitationRequestSerializer,
)
from modules.companies.application.dto.accept_invitation_command import (
    AcceptInvitationCommand,
)
from modules.companies.application.exceptions import (
    InvalidInvitationError,
    InvitationAccountMismatchError,
)
from modules.companies.application.use_cases.accept_invitation_use_case import (
    AcceptInvitationUseCase,
)
from modules.companies.infrastructure.audit.django_audit_event_recorder import (
    DjangoAuditEventRecorder,
)
from modules.companies.infrastructure.persistence.django_invitation_acceptance_repository import (
    DjangoInvitationAcceptanceRepository,
)
from modules.companies.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork


class InvitationAcceptView(APIView):
    def post(self, request) -> Response:
        serializer = AcceptInvitationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            membership = AcceptInvitationUseCase(
                DjangoInvitationAcceptanceRepository(),
                DjangoAuditEventRecorder(),
                DjangoUnitOfWork(),
            ).execute(
                AcceptInvitationCommand(
                    user_id=request.user.id,
                    token=serializer.validated_data["token"],
                ),
                timezone.now(),
            )
        except InvalidInvitationError as exc:
            raise ValidationError("Convite inválido, expirado ou já utilizado.") from exc
        except InvitationAccountMismatchError as exc:
            raise ValidationError("O convite pertence a outra conta.") from exc
        return Response(
            {
                "company_id": str(membership.company_id),
                "role": membership.role,
                "status": membership.status,
            }
        )
