from abc import ABC, abstractmethod
from uuid import UUID

from modules.projects.application.dto.client_summary import ClientSummary
from modules.projects.domain.value_objects.normalized_name import NormalizedName


class ClientRepository(ABC):
    @abstractmethod
    def list_active(self, company_id: UUID) -> list[ClientSummary]:
        raise NotImplementedError

    @abstractmethod
    def create(self, company_id: UUID, name: NormalizedName) -> ClientSummary:
        raise NotImplementedError
