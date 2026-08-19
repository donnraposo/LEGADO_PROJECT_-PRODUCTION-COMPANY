from abc import ABC, abstractmethod
from uuid import UUID

from legado_agent.domain.agent_command import AgentCommand


class LocalRepository(ABC):
    @abstractmethod
    def installation_id(self) -> UUID:
        raise NotImplementedError

    @abstractmethod
    def machine_id(self, company_id: UUID) -> UUID | None:
        raise NotImplementedError

    @abstractmethod
    def bind_machine(self, company_id: UUID, machine_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_commands(self, company_id: UUID, commands: list[AgentCommand]) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_command(self, company_id: UUID, command: AgentCommand) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_commands(self, company_id: UUID) -> list[AgentCommand]:
        raise NotImplementedError

    @abstractmethod
    def last_sequence(self, company_id: UUID) -> int:
        raise NotImplementedError
