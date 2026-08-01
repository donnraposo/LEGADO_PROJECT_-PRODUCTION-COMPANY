from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.company_context import require_owner
from modules.companies.adapters.api.membership_collection_view import (
    MembershipCollectionView,
)
from modules.companies.adapters.api.serializers.update_membership_request_serializer import (
    UpdateMembershipRequestSerializer,
)
from modules.companies.domain.value_objects.membership_role import MembershipRole
from modules.companies.domain.value_objects.membership_status import MembershipStatus
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel


class MembershipDetailView(APIView):
    def patch(self, request, membership_id) -> Response:
        owner = require_owner(request)
        serializer = UpdateMembershipRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            membership = (
                MembershipModel.objects.select_for_update()
                .filter(
                    id=membership_id,
                    company_id=owner.company_id,
                )
                .first()
            )
            if membership is None:
                raise NotFound("Membro não encontrado.")
            new_role = serializer.validated_data.get("role", membership.role)
            new_status = serializer.validated_data.get("status", membership.status)
            removes_owner = membership.role == MembershipRole.OWNER and (
                new_role != MembershipRole.OWNER or new_status != MembershipStatus.ACTIVE
            )
            if (
                removes_owner
                and not MembershipModel.objects.filter(
                    company_id=owner.company_id,
                    role=MembershipRole.OWNER,
                    status=MembershipStatus.ACTIVE,
                )
                .exclude(id=membership.id)
                .exists()
            ):
                raise ValidationError("A empresa deve manter ao menos um Proprietário ativo.")
            membership.role = new_role
            membership.status = new_status
            membership.version += 1
            membership.save(update_fields=["role", "status", "version", "updated_at"])
        return Response(MembershipCollectionView.serialize(membership))
