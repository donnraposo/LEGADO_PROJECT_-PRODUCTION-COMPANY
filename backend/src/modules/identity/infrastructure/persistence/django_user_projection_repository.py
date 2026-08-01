from django.db import transaction

from modules.identity.application.dto.authenticated_identity import AuthenticatedIdentity
from modules.identity.application.ports.user_projection_repository import (
    UserProjectionRepository,
)
from modules.identity.domain.entities.user_projection import UserProjection
from modules.identity.domain.value_objects.email_address import EmailAddress
from modules.identity.infrastructure.cryptography.personal_data_protector import (
    PersonalDataProtector,
)
from modules.identity.infrastructure.persistence.models.user_projection_model import (
    UserProjectionModel,
)


class DjangoUserProjectionRepository(UserProjectionRepository):
    def __init__(self, protector: PersonalDataProtector) -> None:
        self._protector = protector

    @transaction.atomic
    def synchronize(self, identity: AuthenticatedIdentity) -> UserProjection:
        email = EmailAddress(identity.email)
        email_lookup = self._protector.exact_lookup(email.value)
        model = UserProjectionModel.objects.filter(
            keycloak_subject=identity.subject
        ).first()

        if model is None:
            model = UserProjectionModel.objects.create(
                keycloak_subject=identity.subject,
                email_ciphertext=self._protector.encrypt(email.value),
                email_lookup_hmac=email_lookup,
            )
        elif model.email_lookup_hmac != email_lookup:
            model.email_ciphertext = self._protector.encrypt(email.value)
            model.email_lookup_hmac = email_lookup
            model.version += 1
            model.save(
                update_fields=[
                    "email_ciphertext",
                    "email_lookup_hmac",
                    "version",
                    "updated_at",
                ]
            )

        return UserProjection(
            id=model.id,
            keycloak_subject=model.keycloak_subject,
            is_active=model.is_active,
        )
