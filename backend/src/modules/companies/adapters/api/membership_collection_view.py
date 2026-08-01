from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.company_context import require_owner
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel


class MembershipCollectionView(APIView):
    def get(self, request) -> Response:
        owner = require_owner(request)
        memberships = MembershipModel.objects.filter(company_id=owner.company_id).order_by(
            "created_at", "id"
        )
        return Response({"items": [self.serialize(item) for item in memberships]})

    @staticmethod
    def serialize(membership: MembershipModel) -> dict[str, object]:
        return {
            "id": str(membership.id),
            "user_id": str(membership.user_id),
            "role": membership.role,
            "status": membership.status,
            "version": membership.version,
        }
