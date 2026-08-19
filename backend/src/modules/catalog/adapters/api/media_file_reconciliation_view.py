from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from config.infrastructure.django_catalog_audit import DjangoCatalogAudit
from config.infrastructure.django_machine_catalog_authorization import (
    DjangoMachineCatalogAuthorization,
)
from config.infrastructure.django_project_catalog_authorization import (
    DjangoProjectCatalogAuthorization,
)
from config.presentation.http.conflict_error import ConflictError
from modules.catalog.adapters.api.media_file_collection_view import MediaFileCollectionView
from modules.catalog.adapters.api.serializers.reconcile_media_file_request_serializer import (
    ReconcileMediaFileRequestSerializer,
)
from modules.catalog.application.dto.reconcile_media_file_command import (
    ReconcileMediaFileCommand,
)
from modules.catalog.application.exceptions import (
    InvalidMediaFileTransitionError,
    MachineCatalogAccessDeniedError,
    MediaFileNotFoundError,
    MediaFileVersionConflictError,
)
from modules.catalog.application.use_cases.reconcile_media_file_use_case import (
    ReconcileMediaFileUseCase,
)
from modules.catalog.infrastructure.persistence.django_catalog_repository import (
    DjangoCatalogRepository,
)
from modules.catalog.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork
from modules.companies.adapters.api.company_context import require_company_membership


class MediaFileReconciliationView(APIView):
    def patch(self, request, media_file_id) -> Response:
        membership = require_company_membership(request)
        serializer = ReconcileMediaFileRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            item = ReconcileMediaFileUseCase(
                DjangoCatalogRepository(),
                DjangoProjectCatalogAuthorization(),
                DjangoMachineCatalogAuthorization(),
                DjangoCatalogAudit(),
                DjangoUnitOfWork(),
            ).execute(
                ReconcileMediaFileCommand(
                    company_id=membership.company_id,
                    media_file_id=media_file_id,
                    machine_id=data["machine_id"],
                    actor_user_id=request.user.id,
                    actor_role=membership.role,
                    expected_version=data["expected_version"],
                    status=data["status"],
                )
            )
        except (MediaFileNotFoundError, MachineCatalogAccessDeniedError) as exc:
            raise NotFound("Arquivo ou máquina não encontrado.") from exc
        except MediaFileVersionConflictError as exc:
            raise ConflictError("Versão do arquivo desatualizada.") from exc
        except InvalidMediaFileTransitionError as exc:
            raise ValidationError("Transição técnica do arquivo inválida.") from exc
        return Response(MediaFileCollectionView._serialize(item))
