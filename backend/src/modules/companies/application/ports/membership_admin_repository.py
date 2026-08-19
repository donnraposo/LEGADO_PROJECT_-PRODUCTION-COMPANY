from abc import ABC, abstractmethod
from uuid import UUID

from modules.companies.application.dto.membership_snapshot import MembershipSnapshot


class MembershipAdminRepository(ABC):
    @abstractmethod
    def list_for_company(self, company_id: UUID) -> list[MembershipSnapshot]:
        raise NotImplementedError

    @abstractmethod
    def get_for_update(self, company_id: UUID, membership_id: UUID) -> MembershipSnapshot | None:
        raise NotImplementedError

    @abstractmethod
    def has_other_active_owner(self, company_id: UUID, membership_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    def save(self, membership: MembershipSnapshot) -> None:
        raise NotImplementedError
