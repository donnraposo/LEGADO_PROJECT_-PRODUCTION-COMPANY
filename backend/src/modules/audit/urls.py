from django.urls import path

from modules.audit.adapters.api.audit_event_collection_view import AuditEventCollectionView

urlpatterns = [
    path("audit-events", AuditEventCollectionView.as_view(), name="audit-event-collection"),
]
