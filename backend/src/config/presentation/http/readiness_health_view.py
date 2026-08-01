from django.core.cache import cache
from django.db import DatabaseError, connections
from django.http import JsonResponse
from django.views import View


class ReadinessHealthView(View):
    def get(self, request) -> JsonResponse:
        checks = {
            "database": self._database_is_ready(),
            "redis": self._redis_is_ready(),
        }
        is_ready = all(checks.values())
        return JsonResponse(
            {"status": "ready" if is_ready else "unavailable", "checks": checks},
            status=200 if is_ready else 503,
        )

    @staticmethod
    def _database_is_ready() -> bool:
        try:
            with connections["default"].cursor() as cursor:
                cursor.execute("SELECT 1")
                return cursor.fetchone() == (1,)
        except DatabaseError:
            return False

    @staticmethod
    def _redis_is_ready() -> bool:
        marker = "health-ready"
        try:
            cache.set(marker, marker, timeout=5)
            return cache.get(marker) == marker
        except Exception:
            return False
