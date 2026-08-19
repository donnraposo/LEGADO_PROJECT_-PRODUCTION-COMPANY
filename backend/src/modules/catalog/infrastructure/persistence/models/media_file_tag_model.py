import uuid

from django.db import models


class MediaFileTagModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    media_file = models.ForeignKey(
        "catalog.MediaFileModel", on_delete=models.CASCADE, related_name="tag_assignments"
    )
    tag = models.ForeignKey(
        "catalog.TagModel", on_delete=models.PROTECT, related_name="media_assignments"
    )
    applied_by_user_id = models.UUIDField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "media_file_tags"
        constraints = [
            models.UniqueConstraint(fields=["media_file", "tag"], name="uq_media_file_tag")
        ]
