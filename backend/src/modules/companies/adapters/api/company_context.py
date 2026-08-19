from uuid import UUID

from rest_framework.exceptions import PermissionDenied, ValidationError

from modules.companies.application.dto.company_context_snapshot import CompanyContextSnapshot
from modules.companies.application.exceptions import CompanyAccessDeniedError, OwnerRequiredError
from modules.companies.application.use_cases.resolve_company_context_use_case import (
    ResolveCompanyContextUseCase,
)
from modules.companies.infrastructure.persistence.django_company_context_repository import (
    DjangoCompanyContextRepository,
)


def require_company_membership(request) -> CompanyContextSnapshot:
    raw_company_id = request.headers.get("X-Company-ID")
    if not raw_company_id:
        raise ValidationError("O cabeçalho X-Company-ID é obrigatório.")
    try:
        company_id = UUID(raw_company_id)
    except ValueError as exc:
        raise ValidationError("X-Company-ID inválido.") from exc
    try:
        return ResolveCompanyContextUseCase(DjangoCompanyContextRepository()).execute(
            company_id, request.user.id
        )
    except CompanyAccessDeniedError as exc:
        raise PermissionDenied("Acesso à empresa negado.") from exc


def require_owner(request) -> CompanyContextSnapshot:
    raw_company_id = request.headers.get("X-Company-ID")
    if not raw_company_id:
        raise ValidationError("O cabeçalho X-Company-ID é obrigatório.")
    try:
        company_id = UUID(raw_company_id)
    except ValueError as exc:
        raise ValidationError("X-Company-ID inválido.") from exc
    try:
        return ResolveCompanyContextUseCase(DjangoCompanyContextRepository()).execute(
            company_id, request.user.id, owner_required=True
        )
    except CompanyAccessDeniedError as exc:
        raise PermissionDenied("Acesso à empresa negado.") from exc
    except OwnerRequiredError as exc:
        raise PermissionDenied("Operação exclusiva de Proprietário.") from exc
