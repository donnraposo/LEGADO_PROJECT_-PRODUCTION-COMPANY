from modules.companies.application.dto.membership_snapshot import MembershipSnapshot
from modules.companies.application.dto.update_membership_command import UpdateMembershipCommand
from modules.companies.application.exceptions import (
    LastActiveOwnerError,
    MembershipNotFoundError,
    MembershipVersionConflictError,
)
from modules.companies.application.ports.audit_event_recorder import AuditEventRecorder
from modules.companies.application.ports.membership_admin_repository import (
    MembershipAdminRepository,
)
from modules.companies.application.ports.unit_of_work import UnitOfWork
from modules.companies.domain.value_objects.membership_role import MembershipRole
from modules.companies.domain.value_objects.membership_status import MembershipStatus


class UpdateMembershipUseCase:
    def __init__(
        self,
        repository: MembershipAdminRepository,
        audit: AuditEventRecorder,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._repository = repository
        self._audit = audit
        self._unit_of_work = unit_of_work

    def execute(self, command: UpdateMembershipCommand) -> MembershipSnapshot:
        with self._unit_of_work:
            membership = self._repository.get_for_update(command.company_id, command.membership_id)
            if membership is None:
                raise MembershipNotFoundError
            if membership.version != command.expected_version:
                raise MembershipVersionConflictError
            new_role = command.role or membership.role
            new_status = command.status or membership.status
            removes_owner = membership.role == MembershipRole.OWNER and (
                new_role != MembershipRole.OWNER or new_status != MembershipStatus.ACTIVE
            )
            if removes_owner and not self._repository.has_other_active_owner(
                command.company_id, membership.id
            ):
                raise LastActiveOwnerError
            before = {"role": membership.role, "status": membership.status}
            membership.role = new_role
            membership.status = new_status
            membership.version += 1
            self._repository.save(membership)
            self._audit.record_membership_updated(
                company_id=command.company_id,
                actor_user_id=command.actor_user_id,
                membership_id=membership.id,
                before=before,
                after={"role": membership.role, "status": membership.status},
            )
            return membership
