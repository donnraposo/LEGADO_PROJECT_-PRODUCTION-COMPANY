import uuid

from django.db import models


class DriveObjectModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_version = models.ForeignKey(
        "catalog.FileVersionModel", on_delete=models.PROTECT, related_name="storage_objects"
    )
    provider = models.CharField(max_length=32, default="GOOGLE_DRIVE")
    external_id = models.CharField(max_length=255, blank=True)
    object_reference = models.CharField(max_length=512, blank=True)
    status = models.CharField(max_length=40, default="PENDING")
    upload_item = models.OneToOneField(
        "uploads.UploadItemModel",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="drive_object",
    )
    account = models.ForeignKey(
        "drive.DriveAccountModel", on_delete=models.PROTECT, null=True, blank=True
    )
    folder = models.ForeignKey(
        "drive.DriveFolderModel", on_delete=models.PROTECT, null=True, blank=True
    )
    name = models.CharField(max_length=255, blank=True)
    size_bytes = models.PositiveBigIntegerField(null=True, blank=True)
    checksum_sha256 = models.CharField(max_length=128, blank=True)
    mime_type = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "drive_objects"
        constraints = [
            models.UniqueConstraint(
                fields=["account", "external_id"], name="uq_drive_object_account_external"
            )
        ]
