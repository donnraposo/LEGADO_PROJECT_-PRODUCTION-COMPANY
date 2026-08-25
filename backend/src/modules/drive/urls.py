from django.urls import path

from modules.drive.adapters.api.views import (
    DriveAccountView,
    DriveAuthorizationView,
    DriveOAuthCallbackView,
)

urlpatterns = [
    path("drive/account", DriveAccountView.as_view(), name="drive-account"),
    path("drive/oauth/authorization", DriveAuthorizationView.as_view(), name="drive-authorization"),
    path("drive/oauth/callback", DriveOAuthCallbackView.as_view(), name="drive-oauth-callback"),
]
