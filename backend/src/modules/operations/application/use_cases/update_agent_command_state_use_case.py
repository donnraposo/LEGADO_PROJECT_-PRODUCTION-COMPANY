from uuid import UUID

from modules.operations.application.dto.agent_command_summary import AgentCommandSummary
from modules.operations.application.ports.operations_repository import OperationsRepository


class UpdateAgentCommandStateUseCase:
    def __init__(self, repository: OperationsRepository) -> None:
        self._repository = repository

    def execute(
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
        normalized_status = new_status.strip().upper()
        return self._repository.update_command_state(
            company_id=company_id,
            user_id=user_id,
            machine_id=machine_id,
            command_id=command_id,
            expected_version=expected_version,
            new_status=normalized_status,
            progress_percent=progress_percent,
            result=result,
            failure_code=failure_code.strip().upper(),
        )
