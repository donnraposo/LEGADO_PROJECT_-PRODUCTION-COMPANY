import mimetypes
from datetime import datetime
from pathlib import Path

from legado_agent.application.ports.metadata_reader import MetadataReader
from legado_agent.domain.file_metadata import FileMetadata


class SystemMetadataReader(MetadataReader):
    def read(self, path: Path) -> FileMetadata:
        details = path.stat()
        media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        file_date = None
        date_source = "UNIDENTIFIED"
        if details.st_ctime > 0:
            file_date = datetime.fromtimestamp(details.st_ctime).date()
            date_source = "FILESYSTEM_CREATION"
        return FileMetadata(
            size_bytes=details.st_size,
            modified_ns=details.st_mtime_ns,
            media_type=media_type,
            file_date=file_date,
            date_source=date_source,
        )
