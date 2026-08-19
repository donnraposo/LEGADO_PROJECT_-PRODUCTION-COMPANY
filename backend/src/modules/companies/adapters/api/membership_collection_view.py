from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.company_context import require_owner
from modules.companies.application.dto.membership_snapshot import MembershipSnapshot
from modules.companies.application.use_cases.list_memberships_use_case import ListMembershipsUseCase
from modules.companies.infrastructure.persistence.django_membership_admin_repository import (
    DjangoMembershipAdminRepository,
)


class MembershipCollectionView(APIView):
    def get(self, request) -> Response:
        owner = require_owner(request)
        memberships = ListMembershipsUseCase(DjangoMembershipAdminRepository()).execute(
            owner.company_id
        )
        return Response({"items": [self.serialize(item) for item in memberships]})

    @staticmethod
    def serialize(membership: MembershipSnapshot) -> dict[str, object]:
        return {
            "id": str(membership.id),
            "user_id": str(membership.user_id),
            "role": membership.role,
            "status": membership.status,
            "version": membership.version,
        }
