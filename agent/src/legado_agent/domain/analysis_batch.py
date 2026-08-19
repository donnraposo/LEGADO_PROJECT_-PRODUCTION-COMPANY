from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AnalysisBatch:
    id: UUID
    company_id: UUID
    client_name: str
    project_id: UUID
    project_name: str
    source_paths: tuple[str, ...]
    destination_root: str
    status: str
    created_at: datetime
