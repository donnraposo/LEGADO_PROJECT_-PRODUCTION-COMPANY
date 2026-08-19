from dataclasses import dataclass

from modules.catalog.application.dto.media_file_summary import MediaFileSummary


@dataclass(frozen=True, slots=True)
class MetadataUpdateResult:
    media_file: MediaFileSummary
    old_state: dict[str, object]
    new_state: dict[str, object]
