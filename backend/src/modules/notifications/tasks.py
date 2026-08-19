from celery import shared_task

from modules.notifications.application.dto.send_invitation_email_command import (
    SendInvitationEmailCommand,
)
from modules.notifications.application.use_cases.send_invitation_email_use_case import (
    SendInvitationEmailUseCase,
)
from modules.notifications.infrastructure.email.django_email_sender import DjangoEmailSender
from modules.notifications.infrastructure.persistence.django_delivery_recorder import (
    DjangoDeliveryRecorder,
)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def send_company_invitation_email(self, email: str, company_name: str, token: str) -> None:
    SendInvitationEmailUseCase(DjangoEmailSender(), DjangoDeliveryRecorder()).execute(
        SendInvitationEmailCommand(
            email=email,
            company_name=company_name,
            token=token,
            task_id=self.request.id or "direct-call",
            attempt_number=self.request.retries + 1,
        )
    )
