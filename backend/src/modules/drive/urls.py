from django.urls import path

from modules.drive.adapters.api.views import (
    DriveAccountView,
    DriveAuthorizationView,
    DriveFolderTreeView,
    DriveOAuthCallbackView,
)

urlpatterns = [
    path("drive/account", DriveAccountView.as_view(), name="drive-account"),
    path("drive/oauth/authorization", DriveAuthorizationView.as_view(), name="drive-authorization"),
    path("drive/oauth/callback", DriveOAuthCallbackView.as_view(), name="drive-oauth-callback"),
    path("drive/folders/ensure", DriveFolderTreeView.as_view(), name="drive-folder-tree"),
]
