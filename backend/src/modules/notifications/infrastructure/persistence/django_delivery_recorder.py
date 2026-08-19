import hashlib
import hmac
from uuid import UUID

from django.conf import settings
from django.utils import timezone

from modules.notifications.application.ports.delivery_recorder import DeliveryRecorder
from modules.notifications.infrastructure.persistence.models.notification_delivery_model import (
    DELIVERY_DELIVERED,
    DELIVERY_FAILED,
    DELIVERY_PROCESSING,
    NotificationDeliveryModel,
)


class DjangoDeliveryRecorder(DeliveryRecorder):
    def start(self, email: str, task_id: str, attempt_number: int) -> UUID:
        lookup = hmac.new(
            settings.PERSONAL_DATA_HMAC_KEY.encode("utf-8"),
            email.strip().casefold().encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        delivery = NotificationDeliveryModel.objects.create(
            notification_type="COMPANY_INVITATION",
            recipient_lookup_hmac=lookup,
            task_id=task_id,
            attempt_number=attempt_number,
            status=DELIVERY_PROCESSING,
        )
        return delivery.id

    def mark_delivered(self, delivery_id: UUID) -> None:
        NotificationDeliveryModel.objects.filter(id=delivery_id).update(
            status=DELIVERY_DELIVERED,
            finished_at=timezone.now(),
        )

    def mark_failed(self, delivery_id: UUID, error_code: str) -> None:
        NotificationDeliveryModel.objects.filter(id=delivery_id).update(
            status=DELIVERY_FAILED,
            error_code=error_code[:160],
            finished_at=timezone.now(),
        )
