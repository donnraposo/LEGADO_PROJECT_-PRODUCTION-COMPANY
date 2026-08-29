import uuid

from django.db import models


class UploadCheckpointModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(
        "uploads.UploadAttemptModel", on_delete=models.PROTECT, related_name="checkpoints"
    )
    sequence = models.PositiveIntegerField()
    confirmed_bytes = models.PositiveBigIntegerField()
    source = models.CharField(max_length=16, default="DRIVE")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "upload_checkpoints"
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "sequence"], name="uq_upload_checkpoint_sequence"
            )
        ]
