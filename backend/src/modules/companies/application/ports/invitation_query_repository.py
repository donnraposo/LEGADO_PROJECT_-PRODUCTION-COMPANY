from abc import ABC, abstractmethod
from uuid import UUID

from modules.companies.application.dto.invitation_summary import InvitationSummary


class InvitationQueryRepository(ABC):
    @abstractmethod
    def list_for_company(self, company_id: UUID) -> list[InvitationSummary]:
        raise NotImplementedError
