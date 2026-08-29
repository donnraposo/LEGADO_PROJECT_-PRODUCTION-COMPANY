import uuid

from django.db import models


class UploadItemModel(models.Model):
    ACTIVE_STATUSES = ["PENDING", "READY", "UPLOADING", "VERIFYING", "PAUSED"]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(
        "uploads.UploadBatchModel", on_delete=models.PROTECT, related_name="items"
    )
    file_version = models.ForeignKey("catalog.FileVersionModel", on_delete=models.PROTECT)
    destination_folder = models.ForeignKey("drive.DriveFolderModel", on_delete=models.PROTECT)
    destination_category = models.CharField(max_length=16)
    final_name = models.CharField(max_length=255)
    size_bytes = models.PositiveBigIntegerField()
    checksum_algorithm = models.CharField(max_length=24)
    checksum_digest = models.CharField(max_length=128)
    position = models.PositiveIntegerField()
    status = models.CharField(max_length=24, default="PENDING", db_index=True)
    version = models.PositiveBigIntegerField(default=1)
    last_control_key = models.CharField(max_length=120, blank=True)
    last_control_action = models.CharField(max_length=16, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "upload_items"
        ordering = ["position", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["batch", "file_version"], name="uq_upload_item_batch_file_version"
            ),
            models.UniqueConstraint(fields=["batch", "position"], name="uq_upload_item_position"),
            models.UniqueConstraint(
                fields=["file_version"],
                condition=models.Q(
                    status__in=["PENDING", "READY", "UPLOADING", "VERIFYING", "PAUSED"]
                ),
                name="uq_upload_item_active_file_version",
            ),
            models.CheckConstraint(
                condition=models.Q(destination_category__in=["ORIGINAIS", "PREVIEWS", "ENTREGAS"]),
                name="ck_upload_item_category",
            ),
        ]
