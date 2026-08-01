import hashlib
import hmac

from cryptography.fernet import Fernet, MultiFernet


class PersonalDataProtector:
    def __init__(self, encryption_keys: list[str], hmac_key: str) -> None:
        if not encryption_keys:
            raise ValueError("Chave de criptografia de dados pessoais ausente.")
        if len(hmac_key.encode("utf-8")) < 32:
            raise ValueError("Chave HMAC de dados pessoais deve possuir ao menos 32 bytes.")
        self._cipher = MultiFernet([Fernet(key.encode("ascii")) for key in encryption_keys])
        self._hmac_key = hmac_key.encode("utf-8")

    def encrypt(self, plaintext: str) -> bytes:
        return self._cipher.encrypt(plaintext.encode("utf-8"))

    def decrypt(self, ciphertext: bytes) -> str:
        return self._cipher.decrypt(ciphertext).decode("utf-8")

    def exact_lookup(self, normalized_value: str) -> str:
        return hmac.new(
            self._hmac_key,
            normalized_value.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
