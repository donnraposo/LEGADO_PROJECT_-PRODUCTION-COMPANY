from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class TagSummary:
    id: UUID
    name: str
    is_system: bool
