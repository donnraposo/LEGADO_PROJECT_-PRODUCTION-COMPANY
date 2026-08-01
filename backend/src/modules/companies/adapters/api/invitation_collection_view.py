import hashlib
import secrets
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.company_context import require_owner
from modules.companies.adapters.api.personal_data_protector_factory import (
    create_personal_data_protector,
)
from modules.companies.adapters.api.serializers.create_invitation_request_serializer import (
    CreateInvitationRequestSerializer,
)
from modules.companies.infrastructure.persistence.models.invitation_model import InvitationModel
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel
from modules.identity.domain.value_objects.email_address import EmailAddress


class InvitationCollectionView(APIView):
    def get(self, request) -> Response:
        membership = require_owner(request)
        invitations = InvitationModel.objects.filter(company_id=membership.company_id)
        return Response({"items": [self._serialize(item) for item in invitations]})

    def post(self, request) -> Response:
        membership = require_owner(request)
        serializer = CreateInvitationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = EmailAddress(serializer.validated_data["email"])
        protector = create_personal_data_protector()
        email_lookup = protector.exact_lookup(email.value)
        if MembershipModel.objects.filter(
            company_id=membership.company_id,
            user__email_lookup_hmac=email_lookup,
            status="ACTIVE",
        ).exists():
            raise ValidationError("Esta conta já é membro ativo da empresa.")
        InvitationModel.objects.filter(
            company_id=membership.company_id,
            email_lookup_hmac=email_lookup,
            accepted_at__isnull=True,
            cancelled_at__isnull=True,
        ).update(cancelled_at=timezone.now())
        token = secrets.token_urlsafe(32)
        invitation = InvitationModel.objects.create(
            company_id=membership.company_id,
            email_ciphertext=protector.encrypt(email.value),
            email_lookup_hmac=email_lookup,
            token_digest=hashlib.sha256(token.encode("utf-8")).hexdigest(),
            role=serializer.validated_data["role"],
            invited_by_user_id=request.user.id,
            expires_at=timezone.now() + timedelta(days=7),
        )
        payload = self._serialize(invitation)
        payload["token"] = token
        return Response(payload, status=status.HTTP_201_CREATED)

    @staticmethod
    def _serialize(invitation: InvitationModel) -> dict[str, object]:
        return {
            "id": str(invitation.id),
            "role": invitation.role,
            "expires_at": invitation.expires_at.isoformat(),
            "accepted_at": (invitation.accepted_at.isoformat() if invitation.accepted_at else None),
            "cancelled_at": (
                invitation.cancelled_at.isoformat() if invitation.cancelled_at else None
            ),
        }
