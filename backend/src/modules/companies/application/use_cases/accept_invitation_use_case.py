import hashlib
from datetime import datetime

from modules.companies.application.dto.accept_invitation_command import (
    AcceptInvitationCommand,
)
from modules.companies.application.dto.accepted_membership import AcceptedMembership
from modules.companies.application.exceptions import (
    InvalidInvitationError,
    InvitationAccountMismatchError,
)
from modules.companies.application.ports.audit_event_recorder import AuditEventRecorder
from modules.companies.application.ports.invitation_acceptance_repository import (
    InvitationAcceptanceRepository,
)
from modules.companies.application.ports.unit_of_work import UnitOfWork


class AcceptInvitationUseCase:
    def __init__(
        self,
        repository: InvitationAcceptanceRepository,
        audit: AuditEventRecorder,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._audit = audit
        self._unit_of_work = unit_of_work

    def execute(self, command: AcceptInvitationCommand, now: datetime) -> AcceptedMembership:
        digest = hashlib.sha256(command.token.encode("utf-8")).hexdigest()
        with self._unit_of_work:
            invitation = self._repository.get_for_update(digest)
            if (
                invitation is None
                or invitation.accepted_at is not None
                or invitation.cancelled_at is not None
                or invitation.expires_at <= now
            ):
                raise InvalidInvitationError
            if self._repository.user_email_lookup(command.user_id) != invitation.email_lookup_hmac:
                raise InvitationAccountMismatchError
            membership = self._repository.activate_membership(
                invitation.company_id, command.user_id, invitation.role
            )
            self._repository.mark_accepted(invitation.id, now)
            self._audit.record_invitation_accepted(
                company_id=invitation.company_id,
                actor_user_id=command.user_id,
                membership_id=membership.id,
                role=membership.role,
                status=membership.status,
            )
            return membership
