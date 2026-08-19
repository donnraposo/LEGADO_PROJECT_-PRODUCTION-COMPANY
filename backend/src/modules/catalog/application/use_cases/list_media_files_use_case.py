import base64
import binascii
from datetime import datetime
from uuid import UUID

from modules.catalog.application.dto.media_file_page import MediaFilePage
from modules.catalog.application.dto.media_file_query import MediaFileQuery
from modules.catalog.application.exceptions import InvalidCatalogCursorError
from modules.catalog.application.ports.catalog_repository import CatalogRepository
from modules.catalog.application.ports.project_catalog_authorization import (
    ProjectCatalogAuthorization,
)


class ListMediaFilesUseCase:
    def __init__(
        self, repository: CatalogRepository, authorization: ProjectCatalogAuthorization
    ) -> None:
        self._repository = repository
        self._authorization = authorization

    def execute(
        self,
        company_id: UUID,
        user_id: UUID,
        role: str,
        *,
        search: str = "",
        project_id: UUID | None = None,
        status: str = "",
        tag_id: UUID | None = None,
        extension: str = "",
        media_type: str = "",
        min_size_bytes: int | None = None,
        max_size_bytes: int | None = None,
        recorded_from: datetime | None = None,
        recorded_to: datetime | None = None,
        created_by_user_id: UUID | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> MediaFilePage:
        project_ids = self._authorization.accessible_project_ids(company_id, user_id, role)
        after_id = self._decode_cursor(cursor) if cursor else None
        items, next_id = self._repository.list_active(
            MediaFileQuery(
                company_id=company_id,
                project_ids=tuple(project_ids),
                search=search.strip(),
                project_id=project_id,
                status=status.strip().upper(),
                tag_id=tag_id,
                extension=extension.strip().lstrip(".").casefold(),
                media_type=media_type.strip(),
                min_size_bytes=min_size_bytes,
                max_size_bytes=max_size_bytes,
                recorded_from=recorded_from,
                recorded_to=recorded_to,
                created_by_user_id=created_by_user_id,
                after_id=after_id,
                limit=limit,
            )
        )
        return MediaFilePage(
            items=items,
            next_cursor=self._encode_cursor(next_id) if next_id else None,
        )

    @staticmethod
    def _encode_cursor(value: UUID) -> str:
        return base64.urlsafe_b64encode(value.bytes).decode().rstrip("=")

    @staticmethod
    def _decode_cursor(value: str) -> UUID:
        try:
            raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
            if len(raw) != 16:
                raise ValueError
            return UUID(bytes=raw)
        except (ValueError, binascii.Error) as exc:
            raise InvalidCatalogCursorError from exc
