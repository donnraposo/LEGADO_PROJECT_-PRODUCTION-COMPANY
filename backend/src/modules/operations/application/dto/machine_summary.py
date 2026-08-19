from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class MachineSummary:
    id: UUID
    installation_id: UUID
    display_name: str
    os_family: str
    agent_version: str
    status: str
    last_seen_at: datetime
