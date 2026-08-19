from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from config.infrastructure.django_machine_catalog_authorization import (
    DjangoMachineCatalogAuthorization,
)
from config.infrastructure.django_project_catalog_authorization import (
    DjangoProjectCatalogAuthorization,
)
from config.presentation.http.conflict_error import ConflictError
from modules.catalog.adapters.api.media_file_collection_view import MediaFileCollectionView
from modules.catalog.adapters.api.serializers.ingest_media_file_request_serializer import (
    IngestMediaFileRequestSerializer,
)
from modules.catalog.application.dto.ingest_media_file_command import IngestMediaFileCommand
from modules.catalog.application.exceptions import (
    CatalogIngestionConflictError,
    CatalogProjectAccessDeniedError,
    MachineCatalogAccessDeniedError,
)
from modules.catalog.application.use_cases.ingest_media_file_use_case import (
    IngestMediaFileUseCase,
)
from modules.catalog.infrastructure.persistence.django_catalog_repository import (
    DjangoCatalogRepository,
)
from modules.catalog.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork
from modules.companies.adapters.api.company_context import require_company_membership


class AgentMediaFileCollectionView(APIView):
    def post(self, request) -> Response:
        membership = require_company_membership(request)
        serializer = IngestMediaFileRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            item, created = IngestMediaFileUseCase(
                DjangoCatalogRepository(),
                DjangoProjectCatalogAuthorization(),
                DjangoMachineCatalogAuthorization(),
                DjangoUnitOfWork(),
            ).execute(
                IngestMediaFileCommand(
                    company_id=membership.company_id,
                    project_id=data["project_id"],
                    machine_id=data["machine_id"],
                    ingestion_id=data["ingestion_id"],
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
        except MachineCatalogAccessDeniedError as exc:
            raise NotFound("Máquina não encontrada.") from exc
        except CatalogIngestionConflictError as exc:
            raise ConflictError("Identificador de ingestão já usado com outros dados.") from exc
        except ValueError as exc:
            raise ValidationError("Metadados de arquivo inválidos.") from exc
        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(MediaFileCollectionView._serialize(item), status=response_status)
