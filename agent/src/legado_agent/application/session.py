from dataclasses import dataclass


@dataclass(slots=True)
class AgentSession:
    access_token: str | None = None

    @property
    def authenticated(self) -> bool:
        return bool(self.access_token)

    def start(self, access_token: str) -> None:
        if not access_token:
            raise ValueError("Token de acesso ausente.")
        self.access_token = access_token

    def clear(self) -> None:
        self.access_token = None
