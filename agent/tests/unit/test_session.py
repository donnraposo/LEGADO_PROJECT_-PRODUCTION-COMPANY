from legado_agent.application.session import AgentSession


def test_session_keeps_token_only_in_memory() -> None:
    session = AgentSession()

    session.start("temporary-token")
    assert session.authenticated

    session.clear()
    assert not session.authenticated
    assert session.access_token is None
