from abc import ABC, abstractmethod


class PersonalDataProtection(ABC):
    @abstractmethod
    def encrypt(self, plaintext: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def exact_lookup(self, normalized_value: str) -> str:
        raise NotImplementedError
