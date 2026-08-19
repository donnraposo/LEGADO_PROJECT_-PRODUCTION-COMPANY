from rest_framework.response import Response
from rest_framework.views import APIView

from modules.audit.application.dto.audit_event_summary import AuditEventSummary
from modules.audit.application.use_cases.list_audit_events_use_case import ListAuditEventsUseCase
from modules.audit.infrastructure.persistence.django_audit_event_query import DjangoAuditEventQuery
from modules.companies.adapters.api.company_context import require_owner


class AuditEventCollectionView(APIView):
    def get(self, request) -> Response:
        owner = require_owner(request)
        events = ListAuditEventsUseCase(DjangoAuditEventQuery()).execute(owner.company_id)
        return Response(
            {
                "items": [self._serialize(event) for event in events],
                "next_cursor": None,
            }
        )

    @staticmethod
    def _serialize(event: AuditEventSummary) -> dict[str, object]:
        return {
            "id": str(event.id),
            "actor_user_id": str(event.actor_user_id),
            "event_type": event.event_type,
            "action_name": event.action_name,
            "description": event.description,
            "subject_type": event.subject_type,
            "subject_id": str(event.subject_id),
            "old_state": event.old_state,
            "new_state": event.new_state,
            "change_state": event.change_state,
            "correlation_id": str(event.correlation_id),
            "occurred_at": event.occurred_at.isoformat(),
        }
