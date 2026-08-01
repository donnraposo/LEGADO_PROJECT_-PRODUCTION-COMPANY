import jwt
from jwt import PyJWKClient


class KeycloakTokenVerifier:
    def __init__(self, issuer: str, jwks_url: str, audience: str) -> None:
        self._issuer = issuer
        self._audience = audience
        self._jwk_client = PyJWKClient(jwks_url, cache_keys=True)

    def verify(self, token: str) -> dict[str, object]:
        signing_key = self._jwk_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=self._audience,
            issuer=self._issuer,
            options={"require": ["exp", "iat", "iss", "sub"]},
        )
