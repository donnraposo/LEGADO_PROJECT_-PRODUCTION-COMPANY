import uuid

from django.db import models

DELIVERY_PROCESSING = "PROCESSING"
DELIVERY_DELIVERED = "DELIVERED"
DELIVERY_FAILED = "FAILED"
DELIVERY_STATUS_CHOICES = (
    (DELIVERY_PROCESSING, "Processing"),
    (DELIVERY_DELIVERED, "Delivered"),
    (DELIVERY_FAILED, "Failed"),
)


class NotificationDeliveryModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification_type = models.CharField(max_length=80)
    recipient_lookup_hmac = models.CharField(max_length=64, db_index=True)
    task_id = models.CharField(max_length=255, db_index=True)
    attempt_number = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES)
    error_code = models.CharField(max_length=160, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notification_deliveries"
        ordering = ["-started_at", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["task_id", "attempt_number"],
                name="uq_notification_delivery_task_attempt",
            )
        ]
