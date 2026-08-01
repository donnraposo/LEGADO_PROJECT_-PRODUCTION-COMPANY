from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    id: UUID

    @property
    def is_authenticated(self) -> bool:
        return True
