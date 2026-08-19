from abc import ABC, abstractmethod
from pathlib import Path


class FileDiscovery(ABC):
    @abstractmethod
    def discover(self, selected_paths: list[Path]) -> list[Path]:
        raise NotImplementedError
