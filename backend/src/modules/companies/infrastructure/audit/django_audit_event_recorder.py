from uuid import UUID

from modules.audit.infrastructure.persistence.audit_recorder import AuditRecorder
from modules.companies.application.ports.audit_event_recorder import AuditEventRecorder


class DjangoAuditEventRecorder(AuditEventRecorder):
    def record_invitation_created(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        invitation_id: UUID,
        role: str,
        expires_at: str,
    ) -> None:
        AuditRecorder.record(
            company_id=company_id,
            actor_user_id=actor_user_id,
            event_type="COMPANY_INVITATION_CREATED",
            subject_type="invitation",
            subject_id=invitation_id,
            new_state={"role": role, "expires_at": expires_at},
        )

    def record_invitation_cancelled(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        invitation_id: UUID,
    ) -> None:
        AuditRecorder.record(
            company_id=company_id,
            actor_user_id=actor_user_id,
            event_type="COMPANY_INVITATION_CANCELLED",
            subject_type="invitation",
            subject_id=invitation_id,
        )

    def record_invitation_accepted(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        membership_id: UUID,
        role: str,
        status: str,
    ) -> None:
        AuditRecorder.record(
            company_id=company_id,
            actor_user_id=actor_user_id,
            event_type="COMPANY_INVITATION_ACCEPTED",
            subject_type="membership",
            subject_id=membership_id,
            new_state={"role": role, "status": status},
        )

    def record_membership_updated(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        membership_id: UUID,
        before: dict[str, object],
        after: dict[str, object],
    ) -> None:
        AuditRecorder.record(
            company_id=company_id,
            actor_user_id=actor_user_id,
            event_type="COMPANY_MEMBERSHIP_UPDATED",
            subject_type="membership",
            subject_id=membership_id,
            old_state=before,
            new_state=after,
        )
