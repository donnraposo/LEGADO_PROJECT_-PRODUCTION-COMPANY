from django.urls import path

from modules.identity.adapters.api.me_view import MeView

urlpatterns = [
    path("me", MeView.as_view(), name="me"),
]
