import os
import stat
from pathlib import Path

from legado_agent.application.ports.file_discovery import FileDiscovery


class SafeFileDiscovery(FileDiscovery):
    _IGNORED_DIRECTORIES = {
        "$recycle.bin",
        "system volume information",
        ".trash",
        ".trashes",
        "lost+found",
    }
    _IGNORED_FILES = {"desktop.ini", "thumbs.db", ".ds_store"}
    _TEMPORARY_SUFFIXES = {".tmp", ".temp", ".part", ".crdownload"}

    def discover(self, selected_paths: list[Path]) -> list[Path]:
        discovered: dict[str, Path] = {}
        for selected in selected_paths:
            path = Path(os.path.abspath(selected))
            if self._is_technical(path):
                continue
            if path.is_file():
                discovered[os.path.normcase(str(path))] = path
                continue
            if not path.is_dir():
                continue
            for root, directories, files in os.walk(path, followlinks=False):
                root_path = Path(root)
                directories[:] = [
                    name for name in directories if not self._is_technical(root_path / name)
                ]
                for name in files:
                    candidate = root_path / name
                    if not self._is_technical(candidate):
                        discovered[os.path.normcase(str(candidate))] = candidate
        return sorted(discovered.values(), key=lambda item: os.path.normcase(str(item)))

    def _is_technical(self, path: Path) -> bool:
        name = path.name.casefold()
        if any(part.casefold() in self._IGNORED_DIRECTORIES for part in path.parts):
            return True
        if name in self._IGNORED_FILES:
            return True
        if name.startswith("~$") or path.suffix.casefold() in self._TEMPORARY_SUFFIXES:
            return True
        if path.is_symlink():
            return True
        try:
            attributes = getattr(path.stat(follow_symlinks=False), "st_file_attributes", 0)
        except OSError:
            return True
        technical_flags = getattr(stat, "FILE_ATTRIBUTE_SYSTEM", 4) | getattr(
            stat, "FILE_ATTRIBUTE_TEMPORARY", 256
        )
        technical_flags |= getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024)
        return bool(attributes & technical_flags)
