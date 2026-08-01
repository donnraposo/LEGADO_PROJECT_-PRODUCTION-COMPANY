from cryptography.fernet import Fernet

from modules.identity.infrastructure.cryptography.personal_data_protector import (
    PersonalDataProtector,
)


class TestPersonalDataProtector:
    def test_encrypts_and_creates_stable_hmac_lookup(self) -> None:
        protector = PersonalDataProtector([Fernet.generate_key().decode()], "h" * 32)
        plaintext = "pessoa@exemplo.com"

        ciphertext = protector.encrypt(plaintext)

        assert plaintext.encode() not in ciphertext
        assert protector.decrypt(ciphertext) == plaintext
        assert protector.exact_lookup(plaintext) == protector.exact_lookup(plaintext)
