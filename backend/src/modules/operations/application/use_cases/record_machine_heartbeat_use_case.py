from uuid import UUID

from modules.operations.application.dto.machine_summary import MachineSummary
from modules.operations.application.ports.operations_repository import OperationsRepository


class RecordMachineHeartbeatUseCase:
    def __init__(self, repository: OperationsRepository) -> None:
        self._repository = repository

    def execute(
        self,
        *,
        company_id: UUID,
        user_id: UUID,
        installation_id: UUID,
        display_name: str,
        os_family: str,
        agent_version: str,
    ) -> MachineSummary:
        return self._repository.heartbeat(
            company_id=company_id,
            user_id=user_id,
            installation_id=installation_id,
            display_name=" ".join(display_name.split()),
            os_family=os_family.strip().upper(),
            agent_version=agent_version.strip(),
        )
