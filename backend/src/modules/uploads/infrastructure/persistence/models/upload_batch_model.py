import uuid

from django.db import models


class UploadBatchModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey("companies.CompanyModel", on_delete=models.PROTECT)
    project = models.ForeignKey("projects.ProjectModel", on_delete=models.PROTECT)
    machine = models.ForeignKey("operations.MachineModel", on_delete=models.PROTECT)
    drive_account = models.ForeignKey("drive.DriveAccountModel", on_delete=models.PROTECT)
    created_by_user_id = models.UUIDField(db_index=True)
    folder_date = models.DateField()
    idempotency_key = models.CharField(max_length=120)
    payload_digest = models.CharField(max_length=64)
    status = models.CharField(max_length=24, default="CREATED", db_index=True)
    total_items = models.PositiveIntegerField()
    total_bytes = models.PositiveBigIntegerField()
    version = models.PositiveBigIntegerField(default=1)
    last_control_key = models.CharField(max_length=120, blank=True)
    last_control_action = models.CharField(max_length=16, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "upload_batches"
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "idempotency_key"],
                name="uq_upload_batch_idempotency",
            ),
            models.CheckConstraint(
                condition=models.Q(total_items__gte=1) & models.Q(total_items__lte=10000),
                name="ck_upload_batch_item_count",
            ),
        ]
