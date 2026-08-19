from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AgentCommandSummary:
    id: UUID
    machine_id: UUID
    command_type: str
    resource_type: str
    resource_id: UUID | None
    payload: dict[str, object]
    sequence: int
    correlation_id: UUID
    status: str
    progress_percent: int
    result: dict[str, object]
    failure_code: str
    version: int
