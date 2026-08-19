from abc import ABC, abstractmethod
from uuid import UUID

from modules.audit.application.dto.audit_event_summary import AuditEventSummary


class AuditEventQuery(ABC):
    @abstractmethod
    def list_recent(self, company_id: UUID, limit: int) -> list[AuditEventSummary]:
        raise NotImplementedError
