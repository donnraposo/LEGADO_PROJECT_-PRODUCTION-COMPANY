from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ClientSummary:
    id: UUID
    name: str
    version: int
