from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ProjectSummary:
    id: UUID
    client_id: UUID
    name: str
    version: int
