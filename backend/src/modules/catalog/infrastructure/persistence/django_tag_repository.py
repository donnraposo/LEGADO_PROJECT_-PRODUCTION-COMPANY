from collections.abc import Collection
from uuid import UUID

from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone

from modules.catalog.application.dto.tag_summary import TagSummary
from modules.catalog.application.exceptions import (
    MediaFileNotFoundError,
    TagNameConflictError,
    TagNotFoundError,
)
from modules.catalog.application.ports.tag_repository import TagRepository
from modules.catalog.infrastructure.persistence.models.media_file_model import MediaFileModel
from modules.catalog.infrastructure.persistence.models.media_file_tag_model import (
    MediaFileTagModel,
)
from modules.catalog.infrastructure.persistence.models.tag_model import TagModel


class DjangoTagRepository(TagRepository):
    def list_available(self, company_id: UUID) -> list[TagSummary]:
        tags = TagModel.objects.filter(
            Q(is_system=True) | Q(company_id=company_id), archived_at__isnull=True
        ).order_by("name", "id")
        return [self._summary(tag) for tag in tags]

    def create_custom(self, company_id: UUID, name: str) -> TagSummary:
        try:
            tag = TagModel.objects.create(
                company_id=company_id,
                name=name,
                normalized_name=name.casefold(),
                is_system=False,
            )
        except IntegrityError as exc:
            raise TagNameConflictError from exc
        return self._summary(tag)

    def archive_custom(self, company_id: UUID, tag_id: UUID) -> None:
        updated = TagModel.objects.filter(
            id=tag_id, company_id=company_id, is_system=False, archived_at__isnull=True
        ).update(archived_at=timezone.now())
        if not updated:
            raise TagNotFoundError

    def assign(
        self,
        *,
        company_id: UUID,
        media_file_id: UUID,
        tag_id: UUID,
        actor_user_id: UUID,
        project_ids: Collection[UUID],
    ) -> bool:
        media = self._media(company_id, media_file_id, project_ids)
        tag = TagModel.objects.filter(
            Q(is_system=True) | Q(company_id=company_id), id=tag_id, archived_at__isnull=True
        ).first()
        if tag is None:
            raise TagNotFoundError
        _, created = MediaFileTagModel.objects.get_or_create(
            media_file=media,
            tag=tag,
            defaults={"applied_by_user_id": actor_user_id},
        )
        return created

    def remove(
        self,
        *,
        company_id: UUID,
        media_file_id: UUID,
        tag_id: UUID,
        project_ids: Collection[UUID],
    ) -> bool:
        media = self._media(company_id, media_file_id, project_ids)
        deleted, _ = MediaFileTagModel.objects.filter(
            media_file=media, tag_id=tag_id
        ).delete()
        return deleted > 0

    @staticmethod
    def _media(
        company_id: UUID, media_file_id: UUID, project_ids: Collection[UUID]
    ) -> MediaFileModel:
        media = MediaFileModel.objects.filter(
            id=media_file_id,
            company_id=company_id,
            project_id__in=project_ids,
            archived_at__isnull=True,
        ).first()
        if media is None:
            raise MediaFileNotFoundError
        return media

    @staticmethod
    def _summary(tag: TagModel) -> TagSummary:
        return TagSummary(id=tag.id, name=tag.name, is_system=tag.is_system)
