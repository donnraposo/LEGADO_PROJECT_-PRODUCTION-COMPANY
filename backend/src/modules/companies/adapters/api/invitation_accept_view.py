import hashlib

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.serializers.accept_invitation_request_serializer import (
    AcceptInvitationRequestSerializer,
)
from modules.companies.infrastructure.persistence.models.invitation_model import InvitationModel
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel
from modules.identity.infrastructure.persistence.models.user_projection_model import (
    UserProjectionModel,
)


class InvitationAcceptView(APIView):
    def post(self, request) -> Response:
        serializer = AcceptInvitationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        digest = hashlib.sha256(serializer.validated_data["token"].encode("utf-8")).hexdigest()
        now = timezone.now()
        with transaction.atomic():
            invitation = (
                InvitationModel.objects.select_for_update()
                .filter(
                    token_digest=digest,
                    accepted_at__isnull=True,
                    cancelled_at__isnull=True,
                    expires_at__gt=now,
                )
                .first()
            )
            if invitation is None:
                raise ValidationError("Convite inválido, expirado ou já utilizado.")
            user = UserProjectionModel.objects.get(id=request.user.id)
            if user.email_lookup_hmac != invitation.email_lookup_hmac:
                raise ValidationError("O convite pertence a outra conta.")
            membership, _ = MembershipModel.objects.update_or_create(
                company_id=invitation.company_id,
                user_id=request.user.id,
                defaults={"role": invitation.role, "status": "ACTIVE"},
            )
            invitation.accepted_at = now
            invitation.save(update_fields=["accepted_at"])
        return Response(
            {
                "company_id": str(membership.company_id),
                "role": membership.role,
                "status": membership.status,
            }
        )
