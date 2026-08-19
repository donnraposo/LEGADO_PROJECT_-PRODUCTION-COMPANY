from dataclasses import dataclass

from modules.catalog.application.dto.media_file_summary import MediaFileSummary


@dataclass(frozen=True, slots=True)
class MediaFileStateUpdateResult:
    media_file: MediaFileSummary
    old_status: str
    new_status: str
    changed: bool
