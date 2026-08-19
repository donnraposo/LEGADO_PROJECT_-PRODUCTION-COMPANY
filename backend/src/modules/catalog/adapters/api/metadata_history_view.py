from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from config.infrastructure.django_catalog_audit import DjangoCatalogAudit
from config.infrastructure.django_project_catalog_authorization import (
    DjangoProjectCatalogAuthorization,
)
from config.presentation.http.conflict_error import ConflictError
from modules.catalog.adapters.api.media_file_collection_view import MediaFileCollectionView
from modules.catalog.adapters.api.serializers.metadata_history_query_serializer import (
    MetadataHistoryQuerySerializer,
)
from modules.catalog.adapters.api.serializers.restore_metadata_request_serializer import (
    RestoreMetadataRequestSerializer,
)
from modules.catalog.application.dto.restore_metadata_command import RestoreMetadataCommand
from modules.catalog.application.exceptions import (
    MediaFileNotFoundError,
    MediaFileVersionConflictError,
    MetadataRestoreDeniedError,
    MetadataVersionNotFoundError,
)
from modules.catalog.application.use_cases.list_metadata_history_use_case import (
    ListMetadataHistoryUseCase,
)
from modules.catalog.application.use_cases.restore_metadata_use_case import (
    RestoreMetadataUseCase,
)
from modules.catalog.infrastructure.persistence.django_catalog_repository import (
    DjangoCatalogRepository,
)
from modules.catalog.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork
from modules.companies.adapters.api.company_context import require_company_membership


class MetadataHistoryView(APIView):
    def get(self, request, media_file_id) -> Response:
        membership = require_company_membership(request)
        serializer = MetadataHistoryQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        try:
            versions, next_version = ListMetadataHistoryUseCase(
                DjangoCatalogRepository(), DjangoProjectCatalogAuthorization()
            ).execute(
                membership.company_id,
                media_file_id,
                request.user.id,
                membership.role,
                after_version=serializer.validated_data["after_version"],
                limit=serializer.validated_data["limit"],
            )
        except MediaFileNotFoundError as exc:
            raise NotFound("Arquivo não encontrado.") from exc
        return Response(
            {
                "items": [
                    {
                        "version": item.version,
                        "actor_user_id": str(item.actor_user_id),
                        "snapshot": item.snapshot,
                        "created_at": item.created_at.isoformat(),
                    }
                    for item in versions
                ],
                "next_version": next_version,
            }
        )


class RestoreMetadataView(APIView):
    def post(self, request, media_file_id, version) -> Response:
        membership = require_company_membership(request)
        serializer = RestoreMetadataRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            item = RestoreMetadataUseCase(
                DjangoCatalogRepository(),
                DjangoProjectCatalogAuthorization(),
                DjangoCatalogAudit(),
                DjangoUnitOfWork(),
            ).execute(
                RestoreMetadataCommand(
                    company_id=membership.company_id,
                    media_file_id=media_file_id,
                    target_version=version,
                    expected_version=serializer.validated_data["expected_version"],
                    actor_user_id=request.user.id,
                    actor_role=membership.role,
                )
            )
        except MetadataRestoreDeniedError as exc:
            raise PermissionDenied("Somente Proprietários podem restaurar metadados.") from exc
        except (MediaFileNotFoundError, MetadataVersionNotFoundError) as exc:
            raise NotFound("Arquivo ou versão não encontrado.") from exc
        except MediaFileVersionConflictError as exc:
            raise ConflictError("Versão do arquivo desatualizada.") from exc
        return Response(MediaFileCollectionView._serialize(item))
