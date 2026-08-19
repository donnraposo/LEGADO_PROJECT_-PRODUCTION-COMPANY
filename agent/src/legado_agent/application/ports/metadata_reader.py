from abc import ABC, abstractmethod
from pathlib import Path

from legado_agent.domain.file_metadata import FileMetadata


class MetadataReader(ABC):
    @abstractmethod
    def read(self, path: Path) -> FileMetadata:
        raise NotImplementedError
