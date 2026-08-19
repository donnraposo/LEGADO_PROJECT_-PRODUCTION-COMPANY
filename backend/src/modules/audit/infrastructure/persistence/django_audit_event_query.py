from uuid import UUID

from modules.audit.application.dto.audit_event_summary import AuditEventSummary
from modules.audit.application.ports.audit_event_query import AuditEventQuery
from modules.audit.infrastructure.persistence.models.audit_event_model import AuditEventModel


class DjangoAuditEventQuery(AuditEventQuery):
    def list_recent(self, company_id: UUID, limit: int) -> list[AuditEventSummary]:
        return [
            self._summary(item)
            for item in AuditEventModel.objects.filter(company_id=company_id)[:limit]
        ]

    @staticmethod
    def _summary(item: AuditEventModel) -> AuditEventSummary:
        return AuditEventSummary(
            item.id,
            item.actor_user_id,
            item.event_type,
            item.action_name,
            item.description,
            item.subject_type,
            item.subject_id,
            item.old_state,
            item.new_state,
            item.change_state,
            item.correlation_id,
            item.occurred_at,
        )
