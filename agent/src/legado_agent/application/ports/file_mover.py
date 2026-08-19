from abc import ABC, abstractmethod
from pathlib import Path
from uuid import UUID


class FileMover(ABC):
    @abstractmethod
    def validate_source(self, path: Path, size_bytes: int, modified_ns: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def choose_destination(
        self, root: Path, relative_path: str, resolution: str, resolved_name: str
    ) -> Path:
        raise NotImplementedError

    @abstractmethod
    def move(
        self,
        source: Path,
        destination: Path,
        checksum_sha256: str,
        size_bytes: int,
        transfer_id: UUID,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def reconcile(
        self, source: Path, destination: Path, checksum_sha256: str, size_bytes: int
    ) -> str:
        raise NotImplementedError
