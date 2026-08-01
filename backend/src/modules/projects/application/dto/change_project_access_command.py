from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ChangeProjectAccessCommand:
    company_id: UUID
    actor_user_id: UUID
    project_id: UUID
    administrator_user_id: UUID
