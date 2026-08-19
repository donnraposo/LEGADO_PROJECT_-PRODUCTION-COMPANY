from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateClientCommand:
    company_id: UUID
    name: str
