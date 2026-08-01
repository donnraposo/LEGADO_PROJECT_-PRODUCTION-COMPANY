from uuid import UUID

from rest_framework.exceptions import PermissionDenied, ValidationError

from modules.companies.domain.value_objects.membership_role import MembershipRole
from modules.companies.domain.value_objects.membership_status import MembershipStatus
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel


def require_company_membership(request) -> MembershipModel:
    raw_company_id = request.headers.get("X-Company-ID")
    if not raw_company_id:
        raise ValidationError("O cabeçalho X-Company-ID é obrigatório.")
    try:
        company_id = UUID(raw_company_id)
    except ValueError as exc:
        raise ValidationError("X-Company-ID inválido.") from exc
    membership = MembershipModel.objects.filter(
        company_id=company_id,
        user_id=request.user.id,
        status=MembershipStatus.ACTIVE,
        company__archived_at__isnull=True,
    ).first()
    if membership is None:
        raise PermissionDenied("Acesso à empresa negado.")
    return membership


def is_owner(membership: MembershipModel) -> bool:
    return membership.role == MembershipRole.OWNER
