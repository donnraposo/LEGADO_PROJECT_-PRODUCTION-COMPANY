from cryptography.fernet import Fernet
from django.test import TestCase

from modules.identity.application.dto.authenticated_identity import AuthenticatedIdentity
from modules.identity.infrastructure.cryptography.personal_data_protector import (
    PersonalDataProtector,
)
from modules.identity.infrastructure.persistence.django_user_projection_repository import (
    DjangoUserProjectionRepository,
)
from modules.identity.infrastructure.persistence.models.user_projection_model import (
    UserProjectionModel,
)


class DjangoUserProjectionRepositoryTest(TestCase):
    def test_stores_email_only_as_ciphertext_and_hmac(self) -> None:
        protector = PersonalDataProtector([Fernet.generate_key().decode()], "h" * 32)
        repository = DjangoUserProjectionRepository(protector)

        user = repository.synchronize(
            AuthenticatedIdentity(subject="keycloak-user-1", email="Pessoa@Exemplo.com")
        )

        model = UserProjectionModel.objects.get(id=user.id)
        assert b"pessoa@exemplo.com" not in bytes(model.email_ciphertext)
        assert protector.decrypt(bytes(model.email_ciphertext)) == "pessoa@exemplo.com"
        assert model.email_lookup_hmac == protector.exact_lookup("pessoa@exemplo.com")
