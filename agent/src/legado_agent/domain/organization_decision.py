from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class OrganizationDecision:
    analysis_item_id: UUID
    action: str
    resolved_name: str = ""
