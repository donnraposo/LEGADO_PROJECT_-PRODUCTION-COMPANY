import uuid

from django.db import models


class UploadAttemptModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(
        "uploads.UploadItemModel", on_delete=models.PROTECT, related_name="attempts"
    )
    sequence = models.PositiveIntegerField()
    status = models.CharField(max_length=24, default="CREATED", db_index=True)
    session_reference_ciphertext = models.BinaryField(blank=True, default=bytes)
    failure_code = models.CharField(max_length=80, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "upload_attempts"
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(fields=["item", "sequence"], name="uq_upload_attempt_sequence"),
            models.UniqueConstraint(
                fields=["item"],
                condition=models.Q(status__in=["CREATED", "ACTIVE", "INTERRUPTED"]),
                name="uq_upload_attempt_active_item",
            ),
        ]
