from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateCompanyCommand:
    actor_user_id: UUID
    name: str
