import uuid

from django.db import models


class FileVersionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    media_file = models.ForeignKey(
        "catalog.MediaFileModel", on_delete=models.PROTECT, related_name="physical_versions"
    )
    sequence = models.PositiveIntegerField()
    size_bytes = models.PositiveBigIntegerField()
    checksum_algorithm = models.CharField(max_length=24)
    checksum_digest = models.CharField(max_length=128)
    ingestion_id = models.UUIDField(null=True, blank=True, unique=True)
    source_machine_id = models.UUIDField(null=True, blank=True)
    source_reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "file_versions"
        constraints = [
            models.UniqueConstraint(
                fields=["media_file", "sequence"], name="uq_file_version_sequence"
            )
        ]
