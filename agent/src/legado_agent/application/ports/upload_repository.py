from abc import ABC, abstractmethod
from uuid import UUID

from legado_agent.domain.upload_job import UploadJob


class UploadRepository(ABC):
    @abstractmethod
    def source_path(self, media_file_id: UUID) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def get(self, item_id: UUID) -> UploadJob | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, job: UploadJob) -> None:
        raise NotImplementedError
