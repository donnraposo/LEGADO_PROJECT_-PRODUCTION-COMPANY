from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from config.infrastructure.django_catalog_audit import DjangoCatalogAudit
from config.infrastructure.django_project_catalog_authorization import (
    DjangoProjectCatalogAuthorization,
)
from config.presentation.http.conflict_error import ConflictError
from modules.catalog.adapters.api.media_file_collection_view import MediaFileCollectionView
from modules.catalog.adapters.api.serializers.update_media_metadata_request_serializer import (
    UpdateMediaMetadataRequestSerializer,
)
from modules.catalog.application.dto.update_media_metadata_command import (
    UpdateMediaMetadataCommand,
)
from modules.catalog.application.exceptions import (
    MediaFileNotFoundError,
    MediaFileVersionConflictError,
)
from modules.catalog.application.use_cases.update_media_metadata_use_case import (
    UpdateMediaMetadataUseCase,
)
from modules.catalog.infrastructure.persistence.django_catalog_repository import (
    DjangoCatalogRepository,
)
from modules.catalog.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork
from modules.companies.adapters.api.company_context import require_company_membership


class MediaFileDetailView(APIView):
    def patch(self, request, media_file_id) -> Response:
        membership = require_company_membership(request)
        serializer = UpdateMediaMetadataRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            item = UpdateMediaMetadataUseCase(
                DjangoCatalogRepository(),
                DjangoProjectCatalogAuthorization(),
                DjangoCatalogAudit(),
                DjangoUnitOfWork(),
            ).execute(
                UpdateMediaMetadataCommand(
                    company_id=membership.company_id,
                    media_file_id=media_file_id,
                    actor_user_id=request.user.id,
                    actor_role=membership.role,
                    expected_version=data["expected_version"],
                    display_name=data.get("display_name"),
                    description=data.get("description"),
                    observations=data.get("observations"),
                    recorded_at=data.get("recorded_at"),
                )
            )
        except MediaFileNotFoundError as exc:
            raise NotFound("Arquivo não encontrado.") from exc
        except MediaFileVersionConflictError as exc:
            raise ConflictError from exc
        return Response(MediaFileCollectionView._serialize(item))
