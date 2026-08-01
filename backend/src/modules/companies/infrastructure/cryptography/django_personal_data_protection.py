from modules.companies.adapters.api.personal_data_protector_factory import (
    create_personal_data_protector,
)
from modules.companies.application.ports.personal_data_protection import (
    PersonalDataProtection,
)


class DjangoPersonalDataProtection(PersonalDataProtection):
    def encrypt(self, plaintext: str) -> bytes:
        return create_personal_data_protector().encrypt(plaintext)

    def exact_lookup(self, normalized_value: str) -> str:
        return create_personal_data_protector().exact_lookup(normalized_value)
