from abc import ABC, abstractmethod


class InvitationDelivery(ABC):
    @abstractmethod
    def schedule(self, email: str, company_name: str, token: str) -> None:
        raise NotImplementedError
