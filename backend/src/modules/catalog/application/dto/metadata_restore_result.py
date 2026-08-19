from dataclasses import dataclass

from modules.catalog.application.dto.media_file_summary import MediaFileSummary


@dataclass(frozen=True, slots=True)
class MetadataRestoreResult:
    media_file: MediaFileSummary
    old_state: dict[str, object]
    new_state: dict[str, object]
    target_version: int
    changed: bool
