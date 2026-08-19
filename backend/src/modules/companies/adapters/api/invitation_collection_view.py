from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.company_context import require_owner
from modules.companies.adapters.api.serializers.create_invitation_request_serializer import (
    CreateInvitationRequestSerializer,
)
from modules.companies.application.dto.create_invitation_command import (
    CreateInvitationCommand,
)
from modules.companies.application.exceptions import ActiveMemberAlreadyExistsError
from modules.companies.application.use_cases.create_invitation_use_case import (
    CreateInvitationUseCase,
)
from modules.companies.application.use_cases.list_invitations_use_case import (
    ListInvitationsUseCase,
)
from modules.companies.infrastructure.audit.django_audit_event_recorder import (
    DjangoAuditEventRecorder,
)
from modules.companies.infrastructure.cryptography.django_personal_data_protection import (
    DjangoPersonalDataProtection,
)
from modules.companies.infrastructure.notifications.celery_invitation_delivery import (
    CeleryInvitationDelivery,
)
from modules.companies.infrastructure.persistence.django_invitation_creation_repository import (
    DjangoInvitationCreationRepository,
)
from modules.companies.infrastructure.persistence.django_invitation_query_repository import (
    DjangoInvitationQueryRepository,
)
from modules.companies.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork


class InvitationCollectionView(APIView):
    def get(self, request) -> Response:
        membership = require_owner(request)
        invitations = ListInvitationsUseCase(DjangoInvitationQueryRepository()).execute(
            membership.company_id
        )
        return Response({"items": [self._serialize(item) for item in invitations]})

    def post(self, request) -> Response:
        membership = require_owner(request)
        serializer = CreateInvitationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            invitation = CreateInvitationUseCase(
                DjangoInvitationCreationRepository(),
                DjangoPersonalDataProtection(),
                CeleryInvitationDelivery(),
                DjangoAuditEventRecorder(),
                DjangoUnitOfWork(),
            ).execute(
                CreateInvitationCommand(
                    company_id=membership.company_id,
                    company_name=membership.company_name,
                    actor_user_id=request.user.id,
                    email=serializer.validated_data["email"],
                    role=serializer.validated_data["role"],
                    created_at=timezone.now(),
                )
            )
        except ActiveMemberAlreadyExistsError as exc:
            raise ValidationError("Esta conta já é membro ativo da empresa.") from exc
        payload = {
            "id": str(invitation.id),
            "role": invitation.role,
            "expires_at": invitation.expires_at.isoformat(),
            "accepted_at": None,
            "cancelled_at": None,
            "token": invitation.token,
        }
        return Response(payload, status=status.HTTP_201_CREATED)

    @staticmethod
    def _serialize(invitation: object) -> dict[str, object]:
        return {
            "id": str(invitation.id),
            "role": invitation.role,
            "expires_at": invitation.expires_at.isoformat(),
            "accepted_at": (invitation.accepted_at.isoformat() if invitation.accepted_at else None),
            "cancelled_at": (
                invitation.cancelled_at.isoformat() if invitation.cancelled_at else None
            ),
        }
