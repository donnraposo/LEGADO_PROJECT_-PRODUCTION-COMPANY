from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from config.infrastructure.django_project_catalog_authorization import (
    DjangoProjectCatalogAuthorization,
)
from modules.catalog.adapters.api.serializers.create_media_file_request_serializer import (
    CreateMediaFileRequestSerializer,
)
from modules.catalog.adapters.api.serializers.list_media_files_query_serializer import (
    ListMediaFilesQuerySerializer,
)
from modules.catalog.application.dto.create_media_file_command import CreateMediaFileCommand
from modules.catalog.application.dto.media_file_summary import MediaFileSummary
from modules.catalog.application.exceptions import (
    CatalogProjectAccessDeniedError,
    InvalidCatalogCursorError,
)
from modules.catalog.application.use_cases.create_media_file_use_case import CreateMediaFileUseCase
from modules.catalog.application.use_cases.list_media_files_use_case import ListMediaFilesUseCase
from modules.catalog.infrastructure.persistence.django_catalog_repository import (
    DjangoCatalogRepository,
)
from modules.catalog.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork
from modules.companies.adapters.api.company_context import require_company_membership


class MediaFileCollectionView(APIView):
    def get(self, request) -> Response:
        membership = require_company_membership(request)
        serializer = ListMediaFilesQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            page = ListMediaFilesUseCase(
                DjangoCatalogRepository(), DjangoProjectCatalogAuthorization()
            ).execute(
                membership.company_id,
                request.user.id,
                membership.role,
                search=data["q"],
                project_id=data.get("project_id"),
                status=data["status"],
                tag_id=data.get("tag_id"),
                extension=data["extension"],
                media_type=data["media_type"],
                min_size_bytes=data.get("min_size_bytes"),
                max_size_bytes=data.get("max_size_bytes"),
                recorded_from=data.get("recorded_from"),
                recorded_to=data.get("recorded_to"),
                created_by_user_id=data.get("created_by_user_id"),
                cursor=data.get("cursor"),
                limit=data["limit"],
            )
        except InvalidCatalogCursorError as exc:
            raise ValidationError("Cursor de catálogo inválido.") from exc
        return Response(
            {
                "items": [self._serialize(item) for item in page.items],
                "next_cursor": page.next_cursor,
            }
        )

    def post(self, request) -> Response:
        membership = require_company_membership(request)
        serializer = CreateMediaFileRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            item = CreateMediaFileUseCase(
                DjangoCatalogRepository(),
                DjangoProjectCatalogAuthorization(),
                DjangoUnitOfWork(),
            ).execute(
                CreateMediaFileCommand(
                    company_id=membership.company_id,
                    project_id=data["project_id"],
                    actor_user_id=request.user.id,
                    actor_role=membership.role,
                    original_name=data["original_name"],
                    media_type=data.get("media_type", ""),
                    size_bytes=data["size_bytes"],
                    checksum_algorithm=data["checksum_algorithm"],
                    checksum_digest=data["checksum_digest"],
                    recorded_at=data.get("recorded_at"),
                )
            )
        except CatalogProjectAccessDeniedError as exc:
            raise PermissionDenied("Acesso ao projeto negado.") from exc
        except ValueError as exc:
            raise ValidationError("Metadados de arquivo inválidos.") from exc
        return Response(self._serialize(item), status=status.HTTP_201_CREATED)

    @staticmethod
    def _serialize(item: MediaFileSummary) -> dict[str, object]:
        return {
            "id": str(item.id),
            "project_id": str(item.project_id),
            "original_name": item.original_name,
            "display_name": item.display_name,
            "media_type": item.media_type,
            "description": item.description,
            "observations": item.observations,
            "size_bytes": item.size_bytes,
            "file_version_id": str(item.file_version_id),
            "source_machine_id": str(item.source_machine_id) if item.source_machine_id else None,
            "checksum": {
                "algorithm": item.checksum_algorithm,
                "digest": item.checksum_digest,
            },
            "recorded_at": item.recorded_at.isoformat() if item.recorded_at else None,
            "status": item.status,
            "version": item.version,
            "tags": [
                {"id": str(tag.id), "name": tag.name, "is_system": tag.is_system}
                for tag in item.tags
            ],
        }
