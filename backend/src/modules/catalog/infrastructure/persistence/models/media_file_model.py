import uuid

from django.db import models
from django.db.models import Q

from modules.catalog.domain.media_file_status import MediaFileStatus


class MediaFileModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.UUIDField(db_index=True)
    project_id = models.UUIDField(db_index=True)
    created_by_user_id = models.UUIDField(db_index=True)
    original_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    extension = models.CharField(max_length=32, blank=True)
    media_type = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    observations = models.TextField(blank=True)
    recorded_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=40,
        default=MediaFileStatus.DISCOVERED,
        choices=[(status.value, status.value) for status in MediaFileStatus],
        db_index=True,
    )
    version = models.PositiveBigIntegerField(default=1)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "media_files"
        ordering = ["display_name", "id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=[status.value for status in MediaFileStatus]),
                name="ck_media_file_status",
            )
        ]
