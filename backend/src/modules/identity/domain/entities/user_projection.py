from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserProjection:
    id: UUID
    keycloak_subject: str
    is_active: bool
