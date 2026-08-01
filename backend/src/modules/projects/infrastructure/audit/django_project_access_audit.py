from uuid import UUID

from modules.audit.infrastructure.persistence.audit_recorder import AuditRecorder
from modules.projects.application.ports.project_access_audit import ProjectAccessAudit


class DjangoProjectAccessAudit(ProjectAccessAudit):
    def record_granted(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        access_id: UUID,
        project_id: UUID,
        user_id: UUID,
    ) -> None:
        AuditRecorder.record(
            company_id=company_id,
            actor_user_id=actor_user_id,
            event_type="PROJECT_ACCESS_GRANTED",
            subject_type="project_access",
            subject_id=access_id,
            new_state={"project_id": str(project_id), "user_id": str(user_id)},
        )

    def record_revoked(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        access_id: UUID,
        project_id: UUID,
        user_id: UUID,
    ) -> None:
        AuditRecorder.record(
            company_id=company_id,
            actor_user_id=actor_user_id,
            event_type="PROJECT_ACCESS_REVOKED",
            subject_type="project_access",
            subject_id=access_id,
            old_state={"project_id": str(project_id), "user_id": str(user_id)},
        )
