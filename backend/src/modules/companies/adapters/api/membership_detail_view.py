from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from config.presentation.http.conflict_error import ConflictError
from modules.companies.adapters.api.company_context import require_owner
from modules.companies.adapters.api.membership_collection_view import (
    MembershipCollectionView,
)
from modules.companies.adapters.api.serializers.update_membership_request_serializer import (
    UpdateMembershipRequestSerializer,
)
from modules.companies.application.dto.update_membership_command import (
    UpdateMembershipCommand,
)
from modules.companies.application.exceptions import (
    LastActiveOwnerError,
    MembershipNotFoundError,
    MembershipVersionConflictError,
)
from modules.companies.application.use_cases.update_membership_use_case import (
    UpdateMembershipUseCase,
)
from modules.companies.infrastructure.audit.django_audit_event_recorder import (
    DjangoAuditEventRecorder,
)
from modules.companies.infrastructure.persistence.django_membership_admin_repository import (
    DjangoMembershipAdminRepository,
)
from modules.companies.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork


class MembershipDetailView(APIView):
    def patch(self, request, membership_id) -> Response:
        owner = require_owner(request)
        serializer = UpdateMembershipRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            membership = UpdateMembershipUseCase(
                DjangoMembershipAdminRepository(),
                DjangoAuditEventRecorder(),
                DjangoUnitOfWork(),
            ).execute(
                UpdateMembershipCommand(
                    company_id=owner.company_id,
                    actor_user_id=request.user.id,
                    membership_id=membership_id,
                    expected_version=serializer.validated_data["expected_version"],
                    role=serializer.validated_data.get("role"),
                    status=serializer.validated_data.get("status"),
                )
            )
        except MembershipNotFoundError as exc:
            raise NotFound("Membro não encontrado.") from exc
        except MembershipVersionConflictError as exc:
            raise ConflictError from exc
        except LastActiveOwnerError as exc:
            raise ValidationError("A empresa deve manter ao menos um Proprietário ativo.") from exc
        return Response(MembershipCollectionView.serialize(membership))
