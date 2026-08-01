from django.http import JsonResponse
from django.views import View


class LiveHealthView(View):
    def get(self, request) -> JsonResponse:
        return JsonResponse({"status": "ok"})
