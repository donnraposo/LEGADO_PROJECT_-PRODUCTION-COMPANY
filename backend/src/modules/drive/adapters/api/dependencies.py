from django.conf import settings

from modules.companies.adapters.api.personal_data_protector_factory import (
    create_personal_data_protector,
)
from modules.drive.application.exceptions import GoogleOAuthNotConfiguredError
from modules.drive.infrastructure.django_drive_service import DjangoDriveService
from modules.drive.infrastructure.google_drive_gateway import GoogleDriveGateway
from modules.drive.infrastructure.google_oauth_gateway import GoogleOAuthGateway


def create_drive_service() -> DjangoDriveService:
    return DjangoDriveService(create_personal_data_protector())


def create_google_oauth_gateway() -> GoogleOAuthGateway:
    if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        raise GoogleOAuthNotConfiguredError("OAuth do Google ainda não foi configurado.")
    return GoogleOAuthGateway(
        settings.GOOGLE_OAUTH_CLIENT_ID,
        settings.GOOGLE_OAUTH_CLIENT_SECRET,
        settings.GOOGLE_OAUTH_REDIRECT_URI,
    )


def create_google_drive_gateway() -> GoogleDriveGateway:
    return GoogleDriveGateway()
