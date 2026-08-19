from abc import ABC, abstractmethod
from uuid import UUID

from modules.companies.application.dto.company_context_snapshot import CompanyContextSnapshot


class CompanyContextRepository(ABC):
    @abstractmethod
    def find_active(self, company_id: UUID, user_id: UUID) -> CompanyContextSnapshot | None:
        raise NotImplementedError
