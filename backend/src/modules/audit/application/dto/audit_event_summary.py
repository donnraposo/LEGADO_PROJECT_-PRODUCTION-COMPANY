from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AuditEventSummary:
    id: UUID
    actor_user_id: UUID
    event_type: str
    action_name: str
    description: str
    subject_type: str
    subject_id: UUID
    old_state: dict | None
    new_state: dict | None
    change_state: dict
    correlation_id: UUID
    occurred_at: datetime
