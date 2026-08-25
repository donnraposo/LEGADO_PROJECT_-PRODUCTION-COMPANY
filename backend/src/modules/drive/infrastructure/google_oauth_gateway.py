import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from modules.drive.application.exceptions import GoogleOAuthExchangeError


@dataclass(frozen=True, slots=True)
class GoogleCredentials:
    provider_account_id: str
    email: str
    refresh_token: str
    granted_scopes: str


class GoogleOAuthGateway:
    AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"
    SCOPES = "openid email https://www.googleapis.com/auth/drive.file"

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri

    def authorization_url(self, state: str) -> str:
        return f"{self.AUTHORIZATION_ENDPOINT}?{
            urlencode(
                {
                    'client_id': self._client_id,
                    'redirect_uri': self._redirect_uri,
                    'response_type': 'code',
                    'scope': self.SCOPES,
                    'access_type': 'offline',
                    'include_granted_scopes': 'true',
                    'prompt': 'consent',
                    'state': state,
                }
            )
        }"

    def exchange_code(self, code: str) -> GoogleCredentials:
        token_payload = self._request_json(
            Request(
                self.TOKEN_ENDPOINT,
                data=urlencode(
                    {
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": self._redirect_uri,
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
        )
        access_token = token_payload.get("access_token")
        refresh_token = token_payload.get("refresh_token")
        if not access_token or not refresh_token:
            raise GoogleOAuthExchangeError("O Google não devolveu as credenciais esperadas.")
        identity = self._request_json(
            Request(
                self.USERINFO_ENDPOINT,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        )
        if not identity.get("sub") or not identity.get("email"):
            raise GoogleOAuthExchangeError("Não foi possível identificar a conta Google.")
        return GoogleCredentials(
            provider_account_id=identity["sub"],
            email=identity["email"],
            refresh_token=refresh_token,
            granted_scopes=token_payload.get("scope", self.SCOPES),
        )

    @staticmethod
    def _request_json(request: Request) -> dict:
        try:
            with urlopen(request, timeout=20) as response:  # noqa: S310
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise GoogleOAuthExchangeError("Falha na comunicação com o Google.") from exc
