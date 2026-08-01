from abc import ABC, abstractmethod
from uuid import UUID


class CompanyMemberAuthorization(ABC):
    @abstractmethod
    def is_active_administrator(self, company_id: UUID, user_id: UUID) -> bool:
        raise NotImplementedError
