import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

django_application = get_asgi_application()

from config.websocket_urls import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_application,
        "websocket": URLRouter(websocket_urlpatterns),
    }
)
