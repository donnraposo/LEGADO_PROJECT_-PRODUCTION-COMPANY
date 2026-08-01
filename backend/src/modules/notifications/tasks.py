from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def send_company_invitation_email(email: str, company_name: str, token: str) -> None:
    invitation_url = f"{settings.INVITATION_PUBLIC_URL}?token={token}"
    send_mail(
        subject=f"Convite para participar de {company_name}",
        message=f"Use este link para aceitar o convite: {invitation_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
