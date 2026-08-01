import pytest

from modules.identity.domain.value_objects.email_address import EmailAddress


class TestEmailAddress:
    def test_normalizes_email_for_exact_lookup(self) -> None:
        email = EmailAddress("  Pessoa@Exemplo.COM ")

        assert email.value == "pessoa@exemplo.com"

    def test_rejects_invalid_email(self) -> None:
        with pytest.raises(ValueError):
            EmailAddress("endereco-invalido")
