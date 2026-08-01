from modules.companies.application.dto.cancel_invitation_command import (
    CancelInvitationCommand,
)
from modules.companies.application.exceptions import PendingInvitationNotFoundError
from modules.companies.application.ports.audit_event_recorder import AuditEventRecorder
from modules.companies.application.ports.invitation_cancellation_repository import (
    InvitationCancellationRepository,
)
from modules.companies.application.ports.unit_of_work import UnitOfWork


class CancelInvitationUseCase:
    def __init__(
        self,
        repository: InvitationCancellationRepository,
        audit: AuditEventRecorder,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._audit = audit
        self._unit_of_work = unit_of_work

    def execute(self, command: CancelInvitationCommand) -> None:
        with self._unit_of_work:
            cancelled = self._repository.cancel_pending(
                command.company_id,
                command.invitation_id,
                command.cancelled_at,
            )
            if not cancelled:
                raise PendingInvitationNotFoundError
            self._audit.record_invitation_cancelled(
                company_id=command.company_id,
                actor_user_id=command.actor_user_id,
                invitation_id=command.invitation_id,
            )
