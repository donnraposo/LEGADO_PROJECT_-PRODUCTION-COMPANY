from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from config.infrastructure.django_catalog_audit import DjangoCatalogAudit
from config.infrastructure.django_project_catalog_authorization import (
    DjangoProjectCatalogAuthorization,
)
from modules.catalog.application.exceptions import MediaFileNotFoundError, TagNotFoundError
from modules.catalog.application.use_cases.assign_media_tag_use_case import (
    AssignMediaTagUseCase,
    RemoveMediaTagUseCase,
)
from modules.catalog.infrastructure.persistence.django_tag_repository import DjangoTagRepository
from modules.catalog.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork
from modules.companies.adapters.api.company_context import require_company_membership


class MediaFileTagView(APIView):
    def put(self, request, media_file_id, tag_id) -> Response:
        self._execute(AssignMediaTagUseCase, request, media_file_id, tag_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, media_file_id, tag_id) -> Response:
        self._execute(RemoveMediaTagUseCase, request, media_file_id, tag_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _execute(use_case_type, request, media_file_id, tag_id) -> None:
        membership = require_company_membership(request)
        try:
            use_case_type(
                DjangoTagRepository(),
                DjangoProjectCatalogAuthorization(),
                DjangoCatalogAudit(),
                DjangoUnitOfWork(),
            ).execute(
                company_id=membership.company_id,
                media_file_id=media_file_id,
                tag_id=tag_id,
                actor_user_id=request.user.id,
                actor_role=membership.role,
            )
        except MediaFileNotFoundError as exc:
            raise NotFound("Arquivo não encontrado.") from exc
        except TagNotFoundError as exc:
            raise NotFound("Tag não encontrada.") from exc
