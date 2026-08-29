import secrets
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

from legado_agent.infrastructure.identity.pkce import (
    create_code_challenge,
    create_code_verifier,
)


class OidcLoginError(Exception):
    pass


class OidcBrowserClient:
    def __init__(self, issuer: str, client_id: str, timeout_seconds: int = 300) -> None:
        self._issuer = issuer.rstrip("/")
        self._client_id = client_id
        self._timeout_seconds = timeout_seconds

    def login(self) -> str:
        verifier = create_code_verifier()
        state = secrets.token_urlsafe(32)
        result: dict[str, str] = {}
        handler = self._handler(result)
        server = HTTPServer(("127.0.0.1", 0), handler)
        server.timeout = self._timeout_seconds
        redirect_uri = f"http://127.0.0.1:{server.server_port}/callback"
        authorization_url = f"{self._issuer}/protocol/openid-connect/auth?{
            urlencode(
                {
                    'client_id': self._client_id,
                    'response_type': 'code',
                    'scope': 'openid profile email',
                    'redirect_uri': redirect_uri,
                    'state': state,
                    'code_challenge': create_code_challenge(verifier),
                    'code_challenge_method': 'S256',
                }
            )
        }"
        try:
            webbrowser.open(authorization_url)
            server.handle_request()
        finally:
            server.server_close()
        if result.get("state") != state or not result.get("code"):
            raise OidcLoginError("Retorno OIDC ausente ou inválido.")
        response = httpx.post(
            f"{self._issuer}/protocol/openid-connect/token",
            data={
                "grant_type": "authorization_code",
                "client_id": self._client_id,
                "redirect_uri": redirect_uri,
                "code": result["code"],
                "code_verifier": verifier,
            },
            timeout=15,
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise OidcLoginError("Provedor não retornou token de acesso.")
        return str(token)

    @staticmethod
    def _handler(result: dict[str, str]):
        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                query = parse_qs(urlparse(self.path).query)
                result["code"] = query.get("code", [""])[0]
                result["state"] = query.get("state", [""])[0]
                body = (
                    "Autenticação concluída. Você pode retornar ao Gerenciador de Áudio Visual."
                ).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: object) -> None:
                return

        return CallbackHandler
