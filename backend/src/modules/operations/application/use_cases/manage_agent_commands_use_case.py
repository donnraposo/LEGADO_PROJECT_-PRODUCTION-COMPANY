from uuid import UUID

from modules.operations.application.dto.agent_command_summary import AgentCommandSummary
from modules.operations.application.ports.operations_repository import OperationsRepository
from modules.operations.application.sensitive_data_policy import SensitiveDataPolicy


class CreateAgentCommandUseCase:
    def __init__(self, repository: OperationsRepository) -> None:
        self._repository = repository

    def execute(
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
        if not command_type.strip() or not resource_type.strip() or not idempotency_key.strip():
            raise ValueError("Command identification is required")
        if SensitiveDataPolicy.contains_forbidden_key(payload):
            raise ValueError("Command payload contains sensitive fields")
        return self._repository.create_command(
            company_id=company_id,
            user_id=user_id,
            machine_id=machine_id,
            command_type=command_type.strip().upper(),
            resource_type=resource_type.strip().upper(),
            resource_id=resource_id,
            payload=payload,
            idempotency_key=idempotency_key.strip(),
        )


class ListPendingAgentCommandsUseCase:
    def __init__(self, repository: OperationsRepository) -> None:
        self._repository = repository

    def execute(
        self,
        company_id: UUID,
        user_id: UUID,
        machine_id: UUID,
        after_sequence: int,
        limit: int,
    ) -> list[AgentCommandSummary]:
        return self._repository.list_pending_commands(
            company_id, user_id, machine_id, after_sequence, limit
        )
