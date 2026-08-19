from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.catalog.application.exceptions import TagManagementDeniedError, TagNotFoundError
from modules.catalog.application.use_cases.manage_tags_use_case import ArchiveCustomTagUseCase
from modules.catalog.infrastructure.persistence.django_tag_repository import DjangoTagRepository
from modules.catalog.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork
from modules.companies.adapters.api.company_context import require_company_membership


class TagDetailView(APIView):
    def delete(self, request, tag_id) -> Response:
        membership = require_company_membership(request)
        try:
            ArchiveCustomTagUseCase(DjangoTagRepository(), DjangoUnitOfWork()).execute(
                membership.company_id, membership.role, tag_id
            )
        except TagManagementDeniedError as exc:
            raise PermissionDenied("Somente Proprietários podem arquivar tags.") from exc
        except TagNotFoundError as exc:
            raise NotFound("Tag personalizada não encontrada.") from exc
        return Response(status=status.HTTP_204_NO_CONTENT)
