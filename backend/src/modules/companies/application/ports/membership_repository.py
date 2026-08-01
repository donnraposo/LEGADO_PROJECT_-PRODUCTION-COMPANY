from abc import ABC, abstractmethod
from uuid import UUID


class MembershipRepository(ABC):
    @abstractmethod
    def add_owner(self, company_id: UUID, user_id: UUID) -> None:
        raise NotImplementedError
