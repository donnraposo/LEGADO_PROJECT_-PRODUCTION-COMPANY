import hashlib
import json
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from modules.operations.application.command_transition_policy import CommandTransitionPolicy
from modules.operations.application.dto.agent_command_summary import AgentCommandSummary
from modules.operations.application.dto.machine_summary import MachineSummary
from modules.operations.application.exceptions import (
    AgentCommandNotFoundError,
    AgentCommandVersionConflictError,
    CommandIdempotencyConflictError,
    InvalidAgentCommandTransitionError,
    MachineNotFoundError,
)
from modules.operations.application.ports.operations_repository import OperationsRepository
from modules.operations.infrastructure.persistence.models.agent_command_model import (
    AgentCommandModel,
)
from modules.operations.infrastructure.persistence.models.machine_model import MachineModel


class DjangoOperationsRepository(OperationsRepository):
    @transaction.atomic
    def heartbeat(
        self,
        *,
        company_id: UUID,
        user_id: UUID,
        installation_id: UUID,
        display_name: str,
        os_family: str,
        agent_version: str,
    ) -> MachineSummary:
        machine, _ = MachineModel.objects.update_or_create(
            company_id=company_id,
            installation_id=installation_id,
            defaults={
                "registered_by_user_id": user_id,
                "display_name": display_name,
                "os_family": os_family,
                "agent_version": agent_version,
                "status": "ONLINE",
                "last_seen_at": timezone.now(),
            },
        )
        return self._machine_summary(machine)

    @transaction.atomic
    def create_command(
        self,
        *,
        company_id: UUID,
        user_id: UUID,
        machine_id: UUID,
        command_type: str,
        resource_type: str,
        resource_id: UUID | None,
        payload: dict[str, object],
        idempotency_key: str,
    ) -> tuple[AgentCommandSummary, bool]:
        digest = self._payload_digest(
            machine_id, command_type, resource_type, resource_id, payload
        )
        existing = AgentCommandModel.objects.filter(
            company_id=company_id, idempotency_key=idempotency_key
        ).first()
        if existing:
            if existing.payload_digest != digest:
                raise CommandIdempotencyConflictError
            return self._command_summary(existing), False
        machine = (
            MachineModel.objects.select_for_update()
            .filter(id=machine_id, company_id=company_id)
            .first()
        )
        if machine is None:
            raise MachineNotFoundError
        machine.command_sequence += 1
        machine.save(update_fields=["command_sequence", "updated_at"])
        command = AgentCommandModel.objects.create(
            company_id=company_id,
            machine=machine,
            created_by_user_id=user_id,
            command_type=command_type,
            resource_type=resource_type,
            resource_id=resource_id,
            payload=payload,
            payload_digest=digest,
            idempotency_key=idempotency_key,
            sequence=machine.command_sequence,
        )
        return self._command_summary(command), True

    def list_pending_commands(
        self,
        company_id: UUID,
        user_id: UUID,
        machine_id: UUID,
        after_sequence: int,
        limit: int,
    ) -> list[AgentCommandSummary]:
        if not MachineModel.objects.filter(
            id=machine_id, company_id=company_id, registered_by_user_id=user_id
        ).exists():
            raise MachineNotFoundError
        commands = AgentCommandModel.objects.filter(
            company_id=company_id,
            machine_id=machine_id,
            sequence__gt=after_sequence,
            status__in=["PENDING", "ACKNOWLEDGED", "RUNNING"],
        ).order_by("sequence")[:limit]
        return [self._command_summary(command) for command in commands]

    @transaction.atomic
    def update_command_state(
        self,
        *,
        company_id: UUID,
        user_id: UUID,
        machine_id: UUID,
        command_id: UUID,
        expected_version: int,
        new_status: str,
        progress_percent: int,
        result: dict[str, object],
        failure_code: str,
    ) -> AgentCommandSummary:
        command = (
            AgentCommandModel.objects.select_for_update()
            .filter(
                id=command_id,
                company_id=company_id,
                machine_id=machine_id,
                machine__registered_by_user_id=user_id,
            )
            .first()
        )
        if command is None:
            raise AgentCommandNotFoundError
        if command.version != expected_version:
            raise AgentCommandVersionConflictError
        CommandTransitionPolicy.validate(command.status, new_status)
        if new_status == "RUNNING" and progress_percent < command.progress_percent:
            raise InvalidAgentCommandTransitionError
        if new_status == "FAILED" and not failure_code:
            raise InvalidAgentCommandTransitionError
        now = timezone.now()
        command.status = new_status
        command.progress_percent = max(command.progress_percent, progress_percent)
        command.result = result
        command.failure_code = failure_code
        command.version += 1
        if new_status == "ACKNOWLEDGED" and command.acknowledged_at is None:
            command.acknowledged_at = now
        if new_status in {"SUCCEEDED", "FAILED", "CANCELLED"}:
            command.completed_at = now
            if new_status == "SUCCEEDED":
                command.progress_percent = 100
        command.save()
        return self._command_summary(command)

    @staticmethod
    def _payload_digest(
        machine_id: UUID,
        command_type: str,
        resource_type: str,
        resource_id: UUID | None,
        payload: dict[str, object],
    ) -> str:
        canonical = json.dumps(
            {
                "machine_id": str(machine_id),
                "command_type": command_type,
                "resource_type": resource_type,
                "resource_id": str(resource_id) if resource_id else None,
                "payload": payload,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode()).hexdigest()

    @staticmethod
    def _machine_summary(machine: MachineModel) -> MachineSummary:
        return MachineSummary(
            id=machine.id,
            installation_id=machine.installation_id,
            display_name=machine.display_name,
            os_family=machine.os_family,
            agent_version=machine.agent_version,
            status=machine.status,
            last_seen_at=machine.last_seen_at,
        )

    @staticmethod
    def _command_summary(command: AgentCommandModel) -> AgentCommandSummary:
        return AgentCommandSummary(
            id=command.id,
            machine_id=command.machine_id,
            command_type=command.command_type,
            resource_type=command.resource_type,
            resource_id=command.resource_id,
            payload=command.payload,
            sequence=command.sequence,
            correlation_id=command.correlation_id,
            status=command.status,
            progress_percent=command.progress_percent,
            result=command.result,
            failure_code=command.failure_code,
            version=command.version,
        )
