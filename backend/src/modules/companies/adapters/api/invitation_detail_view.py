from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.company_context import require_owner
from modules.companies.infrastructure.persistence.models.invitation_model import InvitationModel


class InvitationDetailView(APIView):
    def delete(self, request, invitation_id) -> Response:
        membership = require_owner(request)
        updated = InvitationModel.objects.filter(
            id=invitation_id,
            company_id=membership.company_id,
            accepted_at__isnull=True,
            cancelled_at__isnull=True,
        ).update(cancelled_at=timezone.now())
        if not updated:
            raise NotFound("Convite pendente não encontrado.")
        return Response(status=status.HTTP_204_NO_CONTENT)
