from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AgentCommand:
    id: UUID
    machine_id: UUID
    command_type: str
    resource_type: str
    resource_id: UUID | None
    payload: dict[str, object]
    sequence: int
    status: str
    progress_percent: int
    version: int
