import uuid

from django.db import models


class MetadataVersionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    media_file = models.ForeignKey(
        "catalog.MediaFileModel", on_delete=models.PROTECT, related_name="metadata_versions"
    )
    version = models.PositiveBigIntegerField()
    actor_user_id = models.UUIDField(db_index=True)
    snapshot = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "metadata_versions"
        ordering = ["version"]
        constraints = [
            models.UniqueConstraint(
                fields=["media_file", "version"], name="uq_metadata_version_number"
            )
        ]
