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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "drive_objects"
