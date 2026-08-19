import pytest
from django.core import mail
from django.test import override_settings

from modules.notifications.infrastructure.persistence.models.notification_delivery_model import (
    DELIVERY_DELIVERED,
    NotificationDeliveryModel,
)
from modules.notifications.tasks import send_company_invitation_email


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    INVITATION_PUBLIC_URL="https://app.example/invitations/accept",
)
@pytest.mark.django_db
def test_invitation_email_contains_single_use_token_link() -> None:
    send_company_invitation_email("member@example.com", "Legado", "secret-token")

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["member@example.com"]
    assert "https://app.example/invitations/accept?token=secret-token" in mail.outbox[0].body
    delivery = NotificationDeliveryModel.objects.get()
    assert delivery.status == DELIVERY_DELIVERED
    assert delivery.attempt_number == 1
    assert delivery.error_code == ""
    assert "member@example.com" not in delivery.recipient_lookup_hmac
