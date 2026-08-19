from abc import ABC, abstractmethod


class EmailSender(ABC):
    @abstractmethod
    def send_company_invitation(self, email: str, company_name: str, token: str) -> None:
        raise NotImplementedError
