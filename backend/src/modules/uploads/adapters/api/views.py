import secrets

from django.core.cache import cache
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.company_context import require_company_membership
from modules.companies.adapters.api.personal_data_protector_factory import (
    create_personal_data_protector,
)
from modules.drive.adapters.api.dependencies import (
    create_google_drive_gateway,
    create_google_oauth_gateway,
)
from modules.drive.application.exceptions import (
    GoogleOAuthExchangeError,
    GoogleOAuthNotConfiguredError,
)
from modules.uploads.adapters.api.serializers.complete_upload_request_serializer import (
    CompleteUploadRequestSerializer,
)
from modules.uploads.adapters.api.serializers.upload_batch_request_serializer import (
    UploadBatchRequestSerializer,
)
from modules.uploads.adapters.api.serializers.upload_checkpoint_request_serializer import (
    UploadCheckpointRequestSerializer,
)
from modules.uploads.adapters.api.serializers.upload_control_request_serializer import (
    UploadControlRequestSerializer,
)
from modules.uploads.adapters.api.serializers.upload_session_request_serializer import (
    UploadSessionRequestSerializer,
)
from modules.uploads.infrastructure.django_upload_completion_service import (
    DjangoUploadCompletionService,
)
from modules.uploads.infrastructure.django_upload_service import (
    DjangoUploadService,
    UploadConflictError,
)
from modules.uploads.infrastructure.django_upload_session_service import (
    DjangoUploadSessionService,
)


class UploadBatchCollectionView(APIView):
    def get(self, request) -> Response:
        membership = require_company_membership(request)
        items = DjangoUploadService().list_batches(
            membership.company_id, request.user.id, membership.role
        )
        return Response({"items": items, "next_cursor": None})

    def post(self, request) -> Response:
        membership = require_company_membership(request)
        serializer = UploadBatchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result, created = DjangoUploadService().create_batch(
                membership.company_id,
                request.user.id,
                membership.role,
                serializer.validated_data["project_id"],
                serializer.validated_data["machine_id"],
                serializer.validated_data["folder_date"],
                serializer.validated_data["idempotency_key"],
                serializer.validated_data["items"],
            )
        except UploadConflictError as exc:
            from config.presentation.http.conflict_error import ConflictError

            raise ConflictError(str(exc)) from exc
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return Response(result, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class UploadRealtimeTicketView(APIView):
    def post(self, request) -> Response:
        membership = require_company_membership(request)
        ticket = secrets.token_urlsafe(32)
        cache.set(
            f"upload-ws-ticket:{ticket}",
            {"company_id": str(membership.company_id), "user_id": str(request.user.id)},
            timeout=60,
        )
        return Response({"ticket": ticket, "expires_in": 60}, status=status.HTTP_201_CREATED)


class UploadBatchDetailView(APIView):
    def get(self, request, batch_id) -> Response:
        membership = require_company_membership(request)
        try:
            result = DjangoUploadService().get_batch(
                membership.company_id, request.user.id, membership.role, batch_id
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return Response(result)


class UploadBatchControlView(APIView):
    def post(self, request, batch_id) -> Response:
        membership = require_company_membership(request)
        serializer = UploadControlRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = DjangoUploadService().control_batch(
                membership.company_id,
                request.user.id,
                membership.role,
                batch_id,
                serializer.validated_data["action"],
                serializer.validated_data["expected_version"],
                serializer.validated_data["idempotency_key"],
            )
        except UploadConflictError as exc:
            from config.presentation.http.conflict_error import ConflictError

            raise ConflictError(str(exc)) from exc
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return Response(result)


class AgentUploadControlView(APIView):
    def get(self, request, item_id) -> Response:
        membership = require_company_membership(request)
        machine_id = request.query_params.get("machine_id")
        if not machine_id:
            raise ValidationError("Máquina ausente.")
        try:
            return Response(
                DjangoUploadService().agent_control(membership.company_id, machine_id, item_id)
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

    def post(self, request, item_id) -> Response:
        membership = require_company_membership(request)
        try:
            result = DjangoUploadService().report_agent_state(
                membership.company_id,
                request.data.get("machine_id"),
                item_id,
                request.data.get("status"),
                int(request.data.get("confirmed_bytes", 0)),
                str(request.data.get("failure_code", "")),
            )
        except UploadConflictError as exc:
            from config.presentation.http.conflict_error import ConflictError

            raise ConflictError(str(exc)) from exc
        except (TypeError, ValueError) as exc:
            raise ValidationError(str(exc)) from exc
        return Response(result)


class UploadAttemptCollectionView(APIView):
    def post(self, request, item_id) -> Response:
        membership = require_company_membership(request)
        try:
            result, created = DjangoUploadService().create_attempt(
                membership.company_id, request.user.id, membership.role, item_id
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return Response(result, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class UploadCheckpointView(APIView):
    def put(self, request, attempt_id) -> Response:
        membership = require_company_membership(request)
        serializer = UploadCheckpointRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = DjangoUploadService().record_checkpoint(
                membership.company_id,
                request.user.id,
                membership.role,
                attempt_id,
                serializer.validated_data["confirmed_bytes"],
            )
        except UploadConflictError as exc:
            from config.presentation.http.conflict_error import ConflictError

            raise ConflictError(str(exc)) from exc
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return Response(result)


class UploadSessionUnavailable(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "Não foi possível preparar a sessão de upload no Google Drive."


class AgentUploadSessionView(APIView):
    def post(self, request, item_id) -> Response:
        membership = require_company_membership(request)
        serializer = UploadSessionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result, created = DjangoUploadSessionService(
                create_personal_data_protector(),
                create_google_oauth_gateway(),
                create_google_drive_gateway(),
            ).ensure_session(
                membership.company_id,
                request.user.id,
                membership.role,
                item_id,
                serializer.validated_data["machine_id"],
            )
        except (GoogleOAuthExchangeError, GoogleOAuthNotConfiguredError) as exc:
            raise UploadSessionUnavailable() from exc
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return Response(result, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class AgentUploadCompletionView(APIView):
    def post(self, request, attempt_id) -> Response:
        membership = require_company_membership(request)
        serializer = CompleteUploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result, created = DjangoUploadCompletionService(
                create_personal_data_protector(),
                create_google_oauth_gateway(),
                create_google_drive_gateway(),
            ).complete(
                membership.company_id,
                request.user.id,
                membership.role,
                attempt_id,
                serializer.validated_data["machine_id"],
                serializer.validated_data["provider_object_id"],
            )
        except (GoogleOAuthExchangeError, GoogleOAuthNotConfiguredError) as exc:
            raise UploadSessionUnavailable() from exc
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return Response(result, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
