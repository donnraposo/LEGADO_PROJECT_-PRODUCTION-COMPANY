from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class OrganizationOperation:
    id: UUID
    batch_id: UUID
    company_id: UUID
    project_id: UUID
    destination_root: str
    status: str
    created_at: datetime
