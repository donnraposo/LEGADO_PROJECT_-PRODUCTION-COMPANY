from abc import ABC, abstractmethod
from uuid import UUID

from modules.companies.application.dto.company_membership_summary import (
    CompanyMembershipSummary,
)
from modules.companies.domain.entities.company import Company
from modules.companies.domain.value_objects.company_name import CompanyName


class CompanyRepository(ABC):
    @abstractmethod
    def create(self, name: CompanyName) -> Company:
        raise NotImplementedError

    @abstractmethod
    def list_active_for_user(self, user_id: UUID) -> list[CompanyMembershipSummary]:
        raise NotImplementedError
