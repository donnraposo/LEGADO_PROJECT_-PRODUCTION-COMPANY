import hashlib
from pathlib import Path

from legado_agent.application.ports.checksum_calculator import ChecksumCalculator


class FileChangedDuringReadError(OSError):
    pass


class StreamingSha256(ChecksumCalculator):
    def __init__(self, chunk_size: int = 4 * 1024 * 1024) -> None:
        if chunk_size < 1:
            raise ValueError("O tamanho do bloco deve ser positivo.")
        self._chunk_size = chunk_size

    def calculate(self, path: Path) -> str:
        before = path.stat()
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while chunk := stream.read(self._chunk_size):
                digest.update(chunk)
        after = path.stat()
        if before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns:
            raise FileChangedDuringReadError("O arquivo foi alterado durante a análise.")
        return digest.hexdigest()
