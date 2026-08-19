from abc import ABC, abstractmethod
from uuid import UUID


class MachineCatalogAuthorization(ABC):
    @abstractmethod
    def is_registered_to_user(self, company_id: UUID, machine_id: UUID, user_id: UUID) -> bool:
        raise NotImplementedError
