from dataclasses import dataclass

from modules.catalog.application.dto.media_file_summary import MediaFileSummary


@dataclass(frozen=True, slots=True)
class MediaFilePage:
    items: list[MediaFileSummary]
    next_cursor: str | None
