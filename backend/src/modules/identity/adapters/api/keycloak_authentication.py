import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from modules.identity.adapters.api.authenticated_principal import AuthenticatedPrincipal
from modules.identity.application.dto.authenticated_identity import AuthenticatedIdentity
from modules.identity.application.use_cases.synchronize_authenticated_user_use_case import (
    SynchronizeAuthenticatedUserUseCase,
)
from modules.identity.infrastructure.cryptography.personal_data_protector import (
    PersonalDataProtector,
)
from modules.identity.infrastructure.oidc.keycloak_token_verifier import (
    KeycloakTokenVerifier,
)
from modules.identity.infrastructure.persistence.django_user_projection_repository import (
    DjangoUserProjectionRepository,
)


class KeycloakAuthentication(BaseAuthentication):
    keyword = b"Bearer"

    def authenticate(self, request):
        authorization = get_authorization_header(request).split()
        if not authorization:
            return None
        if len(authorization) != 2 or authorization[0] != self.keyword:
            raise AuthenticationFailed("Cabeçalho de autenticação inválido.")

        try:
            token = authorization[1].decode("ascii")
            claims = KeycloakTokenVerifier(
                issuer=settings.KEYCLOAK_ISSUER,
                jwks_url=settings.KEYCLOAK_JWKS_URL,
                audience=settings.KEYCLOAK_AUDIENCE,
            ).verify(token)
            subject = str(claims["sub"])
            email = str(claims["email"])
            if claims.get("email_verified") is not True:
                raise AuthenticationFailed("E-mail ainda não verificado.")
            protector = PersonalDataProtector(
                settings.PERSONAL_DATA_ENCRYPTION_KEYS,
                settings.PERSONAL_DATA_HMAC_KEY,
            )
            user = SynchronizeAuthenticatedUserUseCase(
                DjangoUserProjectionRepository(protector)
            ).execute(AuthenticatedIdentity(subject=subject, email=email))
        except AuthenticationFailed:
            raise
        except (KeyError, UnicodeDecodeError, ValueError, jwt.PyJWTError) as error:
            raise AuthenticationFailed("Token inválido ou expirado.") from error

        if not user.is_active:
            raise AuthenticationFailed("Sessão revogada.", code="SESSION_REVOKED")
        return AuthenticatedPrincipal(id=user.id), token
