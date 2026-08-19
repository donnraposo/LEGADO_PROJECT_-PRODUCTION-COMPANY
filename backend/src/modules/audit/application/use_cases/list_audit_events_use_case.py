from uuid import UUID

from modules.audit.application.dto.audit_event_summary import AuditEventSummary
from modules.audit.application.ports.audit_event_query import AuditEventQuery


class ListAuditEventsUseCase:
    def __init__(self, query: AuditEventQuery) -> None:
        self._query = query

    def execute(self, company_id: UUID) -> list[AuditEventSummary]:
        return self._query.list_recent(company_id, 100)
