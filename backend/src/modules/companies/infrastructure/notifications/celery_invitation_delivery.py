from django.db import transaction

from modules.companies.application.ports.invitation_delivery import InvitationDelivery
from modules.notifications.tasks import send_company_invitation_email


class CeleryInvitationDelivery(InvitationDelivery):
    def schedule(self, email: str, company_name: str, token: str) -> None:
        transaction.on_commit(
            lambda: send_company_invitation_email.delay(email, company_name, token)
        )
