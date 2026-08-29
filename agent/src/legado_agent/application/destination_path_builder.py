import re
from datetime import date
from pathlib import PureWindowsPath

_INVALID_CHARACTERS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


def build_destination_path(
    client_name: str, project_name: str, file_date: date | None, file_name: str
) -> str:
    segments = [_safe_segment(client_name), _safe_segment(project_name)]
    if file_date is None:
        segments.append("DATA_NAO_IDENTIFICADA")
    else:
        segments.extend([str(file_date.year), f"{file_date.month:02d}", f"{file_date.day:02d}"])
    segments.append(file_name)
    return str(PureWindowsPath(*segments))


def _safe_segment(value: str) -> str:
    normalized = _INVALID_CHARACTERS.sub("_", value).strip().rstrip(".")
    if not normalized:
        return "SEM_NOME"
    if normalized.upper() in _RESERVED_NAMES:
        return f"_{normalized}"
    return normalized
