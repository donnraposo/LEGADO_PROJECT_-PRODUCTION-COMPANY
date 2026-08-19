from django.urls import path

from modules.catalog.adapters.api.agent_media_file_collection_view import (
    AgentMediaFileCollectionView,
)
from modules.catalog.adapters.api.media_file_collection_view import MediaFileCollectionView
from modules.catalog.adapters.api.media_file_detail_view import MediaFileDetailView
from modules.catalog.adapters.api.media_file_reconciliation_view import (
    MediaFileReconciliationView,
)
from modules.catalog.adapters.api.media_file_tag_view import MediaFileTagView
from modules.catalog.adapters.api.metadata_history_view import (
    MetadataHistoryView,
    RestoreMetadataView,
)
from modules.catalog.adapters.api.tag_collection_view import TagCollectionView
from modules.catalog.adapters.api.tag_detail_view import TagDetailView

urlpatterns = [
    path(
        "agent/media-files",
        AgentMediaFileCollectionView.as_view(),
        name="agent-media-file-collection",
    ),
    path("media-files", MediaFileCollectionView.as_view(), name="media-file-collection"),
    path(
        "media-files/<uuid:media_file_id>",
        MediaFileDetailView.as_view(),
        name="media-file-detail",
    ),
    path("tags", TagCollectionView.as_view(), name="tag-collection"),
    path("tags/<uuid:tag_id>", TagDetailView.as_view(), name="tag-detail"),
    path(
        "media-files/<uuid:media_file_id>/tags/<uuid:tag_id>",
        MediaFileTagView.as_view(),
        name="media-file-tag",
    ),
    path(
        "agent/media-files/<uuid:media_file_id>/state",
        MediaFileReconciliationView.as_view(),
        name="media-file-reconciliation",
    ),
    path(
        "media-files/<uuid:media_file_id>/metadata-history",
        MetadataHistoryView.as_view(),
        name="metadata-history",
    ),
    path(
        "media-files/<uuid:media_file_id>/metadata-history/<int:version>/restore",
        RestoreMetadataView.as_view(),
        name="metadata-restore",
    ),
]
