from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class MetadataVersionSummary:
    version: int
    actor_user_id: UUID
    snapshot: dict[str, object]
    created_at: datetime
