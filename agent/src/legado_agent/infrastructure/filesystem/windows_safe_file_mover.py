import ctypes
import hashlib
import os
import re
import stat
from pathlib import Path, PureWindowsPath
from uuid import UUID

from legado_agent.application.ports.file_mover import FileMover


class WindowsSafeFileMover(FileMover):
    _INVALID_NAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

    def __init__(self, chunk_size: int = 4 * 1024 * 1024) -> None:
        self._chunk_size = chunk_size

    def validate_source(self, path: Path, size_bytes: int, modified_ns: int) -> None:
        details = path.stat()
        if not path.is_file() or path.is_symlink():
            raise OSError("A origem não é um arquivo regular disponível.")
        if details.st_size != size_bytes or details.st_mtime_ns != modified_ns:
            raise OSError("O arquivo mudou desde a prévia; execute nova análise.")

    def choose_destination(
        self, root: Path, relative_path: str, resolution: str, resolved_name: str
    ) -> Path:
        root = root.absolute()
        self._ensure_safe_directory(root, root)
        parts = list(PureWindowsPath(relative_path).parts)
        if not parts:
            raise ValueError("Destino relativo ausente.")
        if resolution == "RENAME":
            parts[-1] = self._validate_name(resolved_name)
        destination = root.joinpath(*parts)
        self._assert_within_root(root, destination)
        self._ensure_safe_directory(root, destination.parent)
        if resolution == "AUTO_RENAME":
            destination = self._available_name(destination)
        elif destination.exists():
            raise FileExistsError("O destino já existe e não será sobrescrito.")
        return destination

    def move(
        self,
        source: Path,
        destination: Path,
        checksum_sha256: str,
        size_bytes: int,
        transfer_id: UUID,
    ) -> str:
        if destination.exists():
            raise FileExistsError("O destino apareceu durante a movimentação.")
        if source.stat().st_size != size_bytes:
            raise OSError("O tamanho da origem mudou antes da movimentação.")
        same_volume = source.stat().st_dev == destination.parent.stat().st_dev
        if same_volume:
            if self._checksum(source) != checksum_sha256:
                raise OSError("O conteúdo da origem mudou desde a análise.")
            self._move_without_replace(source, destination)
            return "MOVED"
        return self._copy_across_volumes(
            source, destination, checksum_sha256, size_bytes, transfer_id
        )

    def reconcile(
        self, source: Path, destination: Path, checksum_sha256: str, size_bytes: int
    ) -> str:
        source_valid = self._matches(source, checksum_sha256, size_bytes)
        destination_valid = self._matches(destination, checksum_sha256, size_bytes)
        if destination_valid and not source.exists():
            return "MOVED"
        if destination_valid and source_valid:
            return "COPIED_SOURCE_REMAINS"
        if source_valid and not destination.exists():
            return "PENDING"
        return "ATTENTION_REQUIRED"

    def _copy_across_volumes(
        self,
        source: Path,
        destination: Path,
        checksum_sha256: str,
        size_bytes: int,
        transfer_id: UUID,
    ) -> str:
        partial = destination.with_name(f".{destination.name}.{transfer_id}.legado-partial")
        digest = hashlib.sha256()
        copied = 0
        partial_created = False
        try:
            with source.open("rb") as input_stream, partial.open("xb") as output_stream:
                partial_created = True
                while chunk := input_stream.read(self._chunk_size):
                    output_stream.write(chunk)
                    digest.update(chunk)
                    copied += len(chunk)
                output_stream.flush()
                os.fsync(output_stream.fileno())
            if copied != size_bytes or digest.hexdigest() != checksum_sha256:
                raise OSError("A cópia não corresponde ao arquivo analisado.")
            self._move_without_replace(partial, destination)
        except Exception:
            if partial_created:
                partial.unlink(missing_ok=True)
            raise
        try:
            source.unlink()
        except OSError:
            return "COPIED_SOURCE_REMAINS"
        return "MOVED"

    def _move_without_replace(self, source: Path, destination: Path) -> None:
        if os.name == "nt":
            moved = ctypes.windll.kernel32.MoveFileW(str(source), str(destination))
            if not moved:
                raise OSError(ctypes.get_last_error(), "Movimentação segura recusada.")
            return
        os.link(source, destination)
        source.unlink()

    def _ensure_safe_directory(self, root: Path, directory: Path) -> None:
        root.mkdir(parents=True, exist_ok=True)
        current = root
        relative = directory.relative_to(root)
        self._reject_reparse_point(root)
        for part in relative.parts:
            current = current / part
            current.mkdir(exist_ok=True)
            self._reject_reparse_point(current)

    @staticmethod
    def _reject_reparse_point(path: Path) -> None:
        details = path.stat(follow_symlinks=False)
        attributes = getattr(details, "st_file_attributes", 0)
        reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024)
        if path.is_symlink() or attributes & reparse:
            raise OSError("O destino contém link ou ponto de nova análise.")
        if not path.is_dir():
            raise NotADirectoryError("O destino não é um diretório.")

    @staticmethod
    def _assert_within_root(root: Path, destination: Path) -> None:
        if os.path.commonpath((root, destination)) != str(root):
            raise ValueError("O destino calculado saiu da pasta-base.")

    def _available_name(self, destination: Path) -> Path:
        if not destination.exists():
            return destination
        stem = destination.stem
        suffix = destination.suffix
        for number in range(1, 100_000):
            candidate = destination.with_name(f"{stem} ({number}){suffix}")
            if not candidate.exists():
                return candidate
        raise FileExistsError("Não foi possível gerar um nome livre no destino.")

    def _validate_name(self, name: str) -> str:
        if not name or name != Path(name).name or self._INVALID_NAME.search(name):
            raise ValueError("O novo nome é inválido para Windows.")
        if name.rstrip(". ") != name:
            raise ValueError("O novo nome termina com caractere inválido.")
        return name

    def _matches(self, path: Path, checksum_sha256: str, size_bytes: int) -> bool:
        try:
            return (
                path.is_file()
                and path.stat().st_size == size_bytes
                and (self._checksum(path) == checksum_sha256)
            )
        except OSError:
            return False

    def _checksum(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while chunk := stream.read(self._chunk_size):
                digest.update(chunk)
        return digest.hexdigest()
