import ssl

from legado_agent.main import ssl_self_test


def test_ssl_self_test_initializes_default_context(monkeypatch) -> None:
    sentinel = object()
    monkeypatch.setattr(ssl, "create_default_context", lambda: sentinel)

    assert ssl_self_test() == 0
