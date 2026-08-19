from abc import ABC, abstractmethod
from uuid import UUID

from modules.operations.application.dto.agent_command_summary import AgentCommandSummary
from modules.operations.application.dto.machine_summary import MachineSummary


class OperationsRepository(ABC):
    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    def list_pending_commands(
        self,
        company_id: UUID,
        user_id: UUID,
        machine_id: UUID,
        after_sequence: int,
        limit: int,
    ) -> list[AgentCommandSummary]:
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError
