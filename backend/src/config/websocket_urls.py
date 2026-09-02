from django.urls import path

from modules.uploads.adapters.websocket import UploadConsumer

websocket_urlpatterns = [
    path("ws/uploads/<str:ticket>", UploadConsumer.as_asgi()),
]
