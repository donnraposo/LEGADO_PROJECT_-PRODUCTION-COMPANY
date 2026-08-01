import hashlib
import secrets
from datetime import timedelta

from modules.companies.application.dto.create_invitation_command import (
    CreateInvitationCommand,
)
from modules.companies.application.dto.created_invitation import CreatedInvitation
from modules.companies.application.exceptions import ActiveMemberAlreadyExistsError
from modules.companies.application.ports.audit_event_recorder import AuditEventRecorder
from modules.companies.application.ports.invitation_creation_repository import (
    InvitationCreationRepository,
)
from modules.companies.application.ports.invitation_delivery import InvitationDelivery
from modules.companies.application.ports.personal_data_protection import (
    PersonalDataProtection,
)
from modules.companies.application.ports.unit_of_work import UnitOfWork
from modules.identity.domain.value_objects.email_address import EmailAddress


class CreateInvitationUseCase:
    def __init__(
        self,
        repository: InvitationCreationRepository,
        protector: PersonalDataProtection,
        delivery: InvitationDelivery,
        audit: AuditEventRecorder,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._protector = protector
        self._delivery = delivery
        self._audit = audit
        self._unit_of_work = unit_of_work

    def execute(self, command: CreateInvitationCommand) -> CreatedInvitation:
        email = EmailAddress(command.email).value
        email_lookup = self._protector.exact_lookup(email)
        if self._repository.active_member_exists(command.company_id, email_lookup):
            raise ActiveMemberAlreadyExistsError
        token = secrets.token_urlsafe(32)
        expires_at = command.created_at + timedelta(days=7)
        with self._unit_of_work:
            self._repository.cancel_pending_for_email(
                command.company_id, email_lookup, command.created_at
            )
            invitation_id = self._repository.create(
                company_id=command.company_id,
                actor_user_id=command.actor_user_id,
                email_ciphertext=self._protector.encrypt(email),
                email_lookup=email_lookup,
                token_digest=hashlib.sha256(token.encode("utf-8")).hexdigest(),
                role=command.role,
                expires_at=expires_at,
            )
            self._audit.record_invitation_created(
                company_id=command.company_id,
                actor_user_id=command.actor_user_id,
                invitation_id=invitation_id,
                role=command.role,
                expires_at=expires_at.isoformat(),
            )
            self._delivery.schedule(command.email, command.company_name, token)
        return CreatedInvitation(
            id=invitation_id,
            role=command.role,
            expires_at=expires_at,
            token=token,
        )
