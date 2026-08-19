from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateProjectCommand:
    company_id: UUID
    client_id: UUID
    actor_user_id: UUID
    actor_role: str
    name: str
