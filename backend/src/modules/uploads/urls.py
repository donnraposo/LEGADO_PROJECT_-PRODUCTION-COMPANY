from django.urls import path

from modules.uploads.adapters.api.views import (
    AgentUploadCompletionView,
    AgentUploadControlView,
    AgentUploadSessionView,
    UploadAttemptCollectionView,
    UploadBatchCollectionView,
    UploadBatchControlView,
    UploadBatchDetailView,
    UploadCheckpointView,
    UploadRealtimeTicketView,
)

urlpatterns = [
    path(
        "agent/upload-items/<uuid:item_id>/control",
        AgentUploadControlView.as_view(),
        name="agent-upload-control",
    ),
    path(
        "agent/upload-attempts/<uuid:attempt_id>/complete",
        AgentUploadCompletionView.as_view(),
        name="agent-upload-complete",
    ),
    path(
        "agent/upload-items/<uuid:item_id>/session",
        AgentUploadSessionView.as_view(),
        name="agent-upload-session",
    ),
    path("upload-batches", UploadBatchCollectionView.as_view(), name="upload-batches"),
    path("upload-realtime/ticket", UploadRealtimeTicketView.as_view(), name="upload-ticket"),
    path("upload-batches/<uuid:batch_id>", UploadBatchDetailView.as_view(), name="upload-batch"),
    path(
        "upload-batches/<uuid:batch_id>/control",
        UploadBatchControlView.as_view(),
        name="upload-batch-control",
    ),
    path(
        "upload-items/<uuid:item_id>/attempts",
        UploadAttemptCollectionView.as_view(),
        name="upload-attempts",
    ),
    path(
        "upload-attempts/<uuid:attempt_id>/checkpoint",
        UploadCheckpointView.as_view(),
        name="upload-checkpoint",
    ),
]
