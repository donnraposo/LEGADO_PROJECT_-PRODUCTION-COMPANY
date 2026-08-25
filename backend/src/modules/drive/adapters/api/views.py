from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.company_context import (
    require_company_membership,
    require_owner,
)
from modules.drive.adapters.api.dependencies import (
    create_drive_service,
    create_google_oauth_gateway,
)
from modules.drive.application.exceptions import (
    GoogleOAuthExchangeError,
    GoogleOAuthNotConfiguredError,
    InvalidOAuthStateError,
)


class GoogleOAuthUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "A conexão com o Google ainda não está configurada."


class DriveAuthorizationView(APIView):
    def post(self, request) -> Response:
        membership = require_owner(request)
        try:
            gateway = create_google_oauth_gateway()
        except GoogleOAuthNotConfiguredError as exc:
            raise GoogleOAuthUnavailable() from exc
        oauth_state = create_drive_service().create_state(membership.company_id, request.user.id)
        return Response({"authorization_url": gateway.authorization_url(oauth_state)})


class DriveOAuthCallbackView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request) -> Response:
        if request.query_params.get("error"):
            return self._frontend_redirect("error")
        code = request.query_params.get("code")
        oauth_state = request.query_params.get("state")
        if not code or not oauth_state:
            return self._frontend_redirect("error")
        try:
            service = create_drive_service()
            saved_state = service.consume_state(oauth_state)
            service.connect(saved_state, create_google_oauth_gateway().exchange_code(code))
        except (
            GoogleOAuthNotConfiguredError,
            GoogleOAuthExchangeError,
            InvalidOAuthStateError,
        ):
            return self._frontend_redirect("error")
        return self._frontend_redirect("connected")

    @staticmethod
    def _frontend_redirect(result: str) -> Response:
        separator = "&" if "?" in settings.GOOGLE_OAUTH_FRONTEND_RETURN_URL else "?"
        return redirect(
            f"{settings.GOOGLE_OAUTH_FRONTEND_RETURN_URL}{separator}{urlencode({'drive': result})}"
        )


class DriveAccountView(APIView):
    def get(self, request) -> Response:
        membership = require_company_membership(request)
        return Response(create_drive_service().summary(membership.company_id))

    def delete(self, request) -> Response:
        membership = require_owner(request)
        create_drive_service().disconnect(membership.company_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
