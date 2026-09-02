import secrets
from collections.abc import AsyncIterator
from urllib.parse import quote

from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from config.infrastructure.django_project_catalog_authorization import (
    DjangoProjectCatalogAuthorization,
)
from modules.catalog.infrastructure.persistence.models import DriveObjectModel
from modules.companies.adapters.api.company_context import require_company_membership
from modules.companies.adapters.api.personal_data_protector_factory import (
    create_personal_data_protector,
)
from modules.drive.adapters.api.dependencies import (
    create_google_drive_gateway,
    create_google_oauth_gateway,
)
from modules.drive.application.exceptions import GoogleOAuthExchangeError

PLAYBACK_TICKET_TTL_SECONDS = 10 * 60


class MediaPlaybackUnavailable(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "Não foi possível carregar o vídeo. Abra o arquivo no Google Drive."


def _authorized_drive_object(company_id, user_id, role, media_file_id):
    project_ids = DjangoProjectCatalogAuthorization().accessible_project_ids(
        company_id, user_id, role
    )
    return (
        DriveObjectModel.objects.select_related("account", "file_version__media_file")
        .filter(
            file_version__media_file_id=media_file_id,
            file_version__media_file__company_id=company_id,
            file_version__media_file__project_id__in=project_ids,
            file_version__media_file__archived_at__isnull=True,
            account__disconnected_at__isnull=True,
            status="CONFIRMED",
        )
        .order_by("-file_version__sequence", "-created_at")
        .first()
    )


class MediaPlaybackTicketView(APIView):
    def post(self, request, media_file_id) -> Response:
        membership = require_company_membership(request)
        drive_object = _authorized_drive_object(
            membership.company_id, request.user.id, membership.role, media_file_id
        )
        if drive_object is None or not drive_object.external_id:
            raise NotFound("Arquivo não disponível no Google Drive.")
        ticket = secrets.token_urlsafe(32)
        cache.set(
            f"media-playback:{ticket}",
            {"drive_object_id": str(drive_object.id)},
            timeout=PLAYBACK_TICKET_TTL_SECONDS,
        )
        provider_id = quote(drive_object.external_id, safe="")
        return Response(
            {
                "stream_url": f"/api/v1/media-playback/{ticket}",
                "download_url": f"/api/v1/media-download/{ticket}",
                "drive_url": f"https://drive.google.com/file/d/{provider_id}/view",
                "expires_in": PLAYBACK_TICKET_TTL_SECONDS,
            },
            status=status.HTTP_201_CREATED,
        )


class MediaPlaybackStreamView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    content_disposition = "inline"

    def get(self, request, ticket):
        payload = cache.get(f"media-playback:{ticket}")
        if not payload:
            raise NotFound("Link de reprodução expirado.")
        drive_object = (
            DriveObjectModel.objects.select_related("account")
            .filter(
                id=payload["drive_object_id"],
                status="CONFIRMED",
                account__disconnected_at__isnull=True,
            )
            .first()
        )
        if drive_object is None or not drive_object.external_id:
            raise NotFound("Arquivo não disponível no Google Drive.")
        try:
            refresh_token = create_personal_data_protector().decrypt(
                bytes(drive_object.account.refresh_token_ciphertext)
            )
            access_token = create_google_oauth_gateway().refresh_access_token(refresh_token)
            upstream = create_google_drive_gateway().open_media(
                access_token,
                drive_object.external_id,
                request.headers.get("Range", ""),
            )
        except GoogleOAuthExchangeError as exc:
            raise MediaPlaybackUnavailable() from exc

        response = StreamingHttpResponse(
            self._chunks(upstream),
            status=getattr(upstream, "status", status.HTTP_200_OK),
            content_type=upstream.headers.get(
                "Content-Type", drive_object.mime_type or "application/octet-stream"
            ),
        )
        for header in ("Content-Length", "Content-Range", "Accept-Ranges"):
            value = upstream.headers.get(header)
            if value:
                response[header] = value
        response["Cache-Control"] = "private, no-store"
        response["Content-Disposition"] = (
            f"{self.content_disposition}; "
            f"filename*=UTF-8''{quote(drive_object.name or 'video', safe='')}"
        )
        return response

    @staticmethod
    async def _chunks(upstream, chunk_size: int = 256 * 1024) -> AsyncIterator[bytes]:
        read = sync_to_async(upstream.read, thread_sensitive=False)
        close = sync_to_async(upstream.close, thread_sensitive=False)
        try:
            while chunk := await read(chunk_size):
                yield chunk
        finally:
            await close()


class MediaDownloadStreamView(MediaPlaybackStreamView):
    content_disposition = "attachment"
