from abc import ABC, abstractmethod
from pathlib import Path


class ChecksumCalculator(ABC):
    @abstractmethod
    def calculate(self, path: Path) -> str:
        raise NotImplementedError
