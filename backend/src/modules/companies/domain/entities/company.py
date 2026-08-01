from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Company:
    id: UUID
    name: str
    archived_at: datetime | None
    version: int
