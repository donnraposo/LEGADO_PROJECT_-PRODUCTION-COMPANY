from abc import ABC, abstractmethod
from uuid import UUID


class DeliveryRecorder(ABC):
    @abstractmethod
    def start(self, email: str, task_id: str, attempt_number: int) -> UUID:
        raise NotImplementedError

    @abstractmethod
    def mark_delivered(self, delivery_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def mark_failed(self, delivery_id: UUID, error_code: str) -> None:
        raise NotImplementedError
