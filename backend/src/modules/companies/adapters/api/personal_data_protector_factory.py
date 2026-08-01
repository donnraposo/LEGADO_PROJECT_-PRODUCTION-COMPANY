from django.conf import settings

from modules.identity.infrastructure.cryptography.personal_data_protector import (
    PersonalDataProtector,
)


def create_personal_data_protector() -> PersonalDataProtector:
    return PersonalDataProtector(
        settings.PERSONAL_DATA_ENCRYPTION_KEYS,
        settings.PERSONAL_DATA_HMAC_KEY,
    )
