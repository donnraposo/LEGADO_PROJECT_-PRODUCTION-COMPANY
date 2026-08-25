from django.urls import include, path

from config.presentation.http.live_health_view import LiveHealthView
from config.presentation.http.readiness_health_view import ReadinessHealthView

urlpatterns = [
    path("health/live", LiveHealthView.as_view(), name="health-live"),
    path("health/ready", ReadinessHealthView.as_view(), name="health-ready"),
    path("api/v1/", include("modules.identity.urls")),
    path("api/v1/", include("modules.companies.urls")),
    path("api/v1/", include("modules.projects.urls")),
    path("api/v1/", include("modules.audit.urls")),
    path("api/v1/", include("modules.catalog.urls")),
    path("api/v1/", include("modules.operations.urls")),
    path("api/v1/", include("modules.drive.urls")),
]
