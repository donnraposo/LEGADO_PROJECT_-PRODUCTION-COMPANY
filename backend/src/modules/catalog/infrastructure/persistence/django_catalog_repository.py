from collections.abc import Collection
from pathlib import PurePath
from uuid import UUID

from django.db import IntegrityError
from django.db.models import Q
from django.utils.dateparse import parse_datetime

from modules.catalog.application.dto.create_media_file_command import CreateMediaFileCommand
from modules.catalog.application.dto.ingest_media_file_command import IngestMediaFileCommand
from modules.catalog.application.dto.media_file_query import MediaFileQuery
from modules.catalog.application.dto.media_file_state_update_result import (
    MediaFileStateUpdateResult,
)
from modules.catalog.application.dto.media_file_summary import MediaFileSummary
from modules.catalog.application.dto.metadata_restore_result import MetadataRestoreResult
from modules.catalog.application.dto.metadata_update_result import MetadataUpdateResult
from modules.catalog.application.dto.metadata_version_summary import MetadataVersionSummary
from modules.catalog.application.dto.reconcile_media_file_command import (
    ReconcileMediaFileCommand,
)
from modules.catalog.application.dto.restore_metadata_command import RestoreMetadataCommand
from modules.catalog.application.dto.tag_summary import TagSummary
from modules.catalog.application.dto.update_media_metadata_command import (
    UpdateMediaMetadataCommand,
)
from modules.catalog.application.exceptions import (
    CatalogIngestionConflictError,
    CatalogIngestionRaceError,
    MediaFileNotFoundError,
    MediaFileVersionConflictError,
    MetadataVersionNotFoundError,
)
from modules.catalog.application.media_file_transition_policy import MediaFileTransitionPolicy
from modules.catalog.application.ports.catalog_repository import CatalogRepository
from modules.catalog.infrastructure.persistence.models.file_version_model import FileVersionModel
from modules.catalog.infrastructure.persistence.models.media_file_model import MediaFileModel
from modules.catalog.infrastructure.persistence.models.metadata_version_model import (
    MetadataVersionModel,
)


class DjangoCatalogRepository(CatalogRepository):
    def create(self, command: CreateMediaFileCommand) -> MediaFileSummary:
        media = MediaFileModel.objects.create(
            company_id=command.company_id,
            project_id=command.project_id,
            created_by_user_id=command.actor_user_id,
            original_name=command.original_name,
            display_name=command.original_name,
            extension=PurePath(command.original_name).suffix.lstrip(".").casefold(),
            media_type=command.media_type,
            recorded_at=command.recorded_at,
        )
        physical = FileVersionModel.objects.create(
            media_file=media,
            sequence=1,
            size_bytes=command.size_bytes,
            checksum_algorithm=command.checksum_algorithm,
            checksum_digest=command.checksum_digest,
        )
        MetadataVersionModel.objects.create(
            media_file=media,
            version=media.version,
            actor_user_id=command.actor_user_id,
            snapshot=self._metadata_state(media),
        )
        return self._summary(media, physical)

    def ingest(self, command: IngestMediaFileCommand) -> tuple[MediaFileSummary, bool]:
        existing = (
            FileVersionModel.objects.select_related("media_file")
            .filter(ingestion_id=command.ingestion_id)
            .first()
        )
        if existing is not None:
            media = existing.media_file
            expected = (
                media.company_id,
                media.project_id,
                existing.source_machine_id,
                media.original_name,
                existing.size_bytes,
                existing.checksum_algorithm,
                existing.checksum_digest,
            )
            received = (
                command.company_id,
                command.project_id,
                command.machine_id,
                command.original_name,
                command.size_bytes,
                command.checksum_algorithm,
                command.checksum_digest,
            )
            if expected != received:
                raise CatalogIngestionConflictError
            return self._summary(media, existing), False
        media = MediaFileModel.objects.create(
            company_id=command.company_id,
            project_id=command.project_id,
            created_by_user_id=command.actor_user_id,
            original_name=command.original_name,
            display_name=command.original_name,
            extension=PurePath(command.original_name).suffix.lstrip(".").casefold(),
            media_type=command.media_type,
            recorded_at=command.recorded_at,
        )
        try:
            physical = FileVersionModel.objects.create(
                media_file=media,
                sequence=1,
                size_bytes=command.size_bytes,
                checksum_algorithm=command.checksum_algorithm,
                checksum_digest=command.checksum_digest,
                ingestion_id=command.ingestion_id,
                source_machine_id=command.machine_id,
            )
        except IntegrityError as exc:
            raise CatalogIngestionRaceError from exc
        MetadataVersionModel.objects.create(
            media_file=media,
            version=media.version,
            actor_user_id=command.actor_user_id,
            snapshot=self._metadata_state(media),
        )
        return self._summary(media, physical), True

    def list_active(self, query: MediaFileQuery) -> tuple[list[MediaFileSummary], UUID | None]:
        if not query.project_ids:
            return [], None
        items = (
            MediaFileModel.objects.filter(
                company_id=query.company_id,
                project_id__in=query.project_ids,
                archived_at__isnull=True,
            )
            .prefetch_related("physical_versions", "tag_assignments__tag")
            .order_by("id")
        )
        if query.search:
            items = items.filter(
                Q(original_name__icontains=query.search)
                | Q(display_name__icontains=query.search)
                | Q(description__icontains=query.search)
                | Q(observations__icontains=query.search)
            )
        if query.project_id:
            items = items.filter(project_id=query.project_id)
        if query.status:
            items = items.filter(status=query.status)
        if query.tag_id:
            items = items.filter(tag_assignments__tag_id=query.tag_id).distinct()
        if query.extension:
            items = items.filter(extension=query.extension)
        if query.media_type:
            items = items.filter(media_type__iexact=query.media_type)
        if query.min_size_bytes is not None:
            items = items.filter(physical_versions__size_bytes__gte=query.min_size_bytes)
        if query.max_size_bytes is not None:
            items = items.filter(physical_versions__size_bytes__lte=query.max_size_bytes)
        if query.recorded_from:
            items = items.filter(recorded_at__gte=query.recorded_from)
        if query.recorded_to:
            items = items.filter(recorded_at__lte=query.recorded_to)
        if query.created_by_user_id:
            items = items.filter(created_by_user_id=query.created_by_user_id)
        items = items.distinct()
        if query.after_id:
            items = items.filter(id__gt=query.after_id)
        page = list(items[: query.limit + 1])
        has_next = len(page) > query.limit
        page = page[: query.limit]
        summaries = [self._summary(item, item.physical_versions.all()[0]) for item in page]
        return summaries, page[-1].id if has_next else None

    def update_metadata(
        self, command: UpdateMediaMetadataCommand, project_ids: Collection[UUID]
    ) -> MetadataUpdateResult:
        media = (
            MediaFileModel.objects.select_for_update()
            .filter(
                id=command.media_file_id,
                company_id=command.company_id,
                project_id__in=project_ids,
                archived_at__isnull=True,
            )
            .first()
        )
        if media is None:
            raise MediaFileNotFoundError
        if media.version != command.expected_version:
            raise MediaFileVersionConflictError
        old_state = self._metadata_state(media)
        if command.display_name is not None:
            media.display_name = command.display_name.strip()
        if command.description is not None:
            media.description = command.description.strip()
        if command.observations is not None:
            media.observations = command.observations.strip()
        if command.recorded_at is not None:
            media.recorded_at = command.recorded_at
        media.version += 1
        media.save(
            update_fields=[
                "display_name",
                "description",
                "observations",
                "recorded_at",
                "version",
                "updated_at",
            ]
        )
        new_state = self._metadata_state(media)
        MetadataVersionModel.objects.create(
            media_file=media,
            version=media.version,
            actor_user_id=command.actor_user_id,
            snapshot=new_state,
        )
        physical = FileVersionModel.objects.filter(media_file=media).order_by("sequence").first()
        return MetadataUpdateResult(
            media_file=self._summary(media, physical),
            old_state=old_state,
            new_state=new_state,
        )

    def reconcile_state(
        self, command: ReconcileMediaFileCommand, project_ids: Collection[UUID]
    ) -> MediaFileStateUpdateResult:
        media = (
            MediaFileModel.objects.select_for_update()
            .filter(
                id=command.media_file_id,
                company_id=command.company_id,
                project_id__in=project_ids,
                archived_at__isnull=True,
            )
            .first()
        )
        if media is None:
            raise MediaFileNotFoundError
        physical = (
            FileVersionModel.objects.select_for_update()
            .filter(media_file=media)
            .order_by("sequence")
            .first()
        )
        if physical is None:
            raise MediaFileNotFoundError
        if physical.source_machine_id not in {None, command.machine_id}:
            raise MediaFileNotFoundError
        if media.status == command.status:
            return MediaFileStateUpdateResult(
                media_file=self._summary(media, physical),
                old_status=media.status,
                new_status=media.status,
                changed=False,
            )
        if media.version != command.expected_version:
            raise MediaFileVersionConflictError
        MediaFileTransitionPolicy.validate(media.status, command.status)
        old_status = media.status
        media.status = command.status
        media.version += 1
        media.save(update_fields=["status", "version", "updated_at"])
        if physical.source_machine_id is None:
            physical.source_machine_id = command.machine_id
            physical.save(update_fields=["source_machine_id"])
        return MediaFileStateUpdateResult(
            media_file=self._summary(media, physical),
            old_status=old_status,
            new_status=media.status,
            changed=True,
        )

    def list_metadata_versions(
        self,
        company_id: UUID,
        media_file_id: UUID,
        project_ids: Collection[UUID],
        after_version: int,
        limit: int,
    ) -> tuple[list[MetadataVersionSummary], int | None]:
        media = MediaFileModel.objects.filter(
            id=media_file_id,
            company_id=company_id,
            project_id__in=project_ids,
            archived_at__isnull=True,
        ).first()
        if media is None:
            raise MediaFileNotFoundError
        versions = list(
            MetadataVersionModel.objects.filter(
                media_file=media, version__gt=after_version
            ).order_by("version")[: limit + 1]
        )
        has_next = len(versions) > limit
        versions = versions[:limit]
        summaries = [
            MetadataVersionSummary(
                version=item.version,
                actor_user_id=item.actor_user_id,
                snapshot=item.snapshot,
                created_at=item.created_at,
            )
            for item in versions
        ]
        return summaries, versions[-1].version if has_next else None

    def restore_metadata(
        self, command: RestoreMetadataCommand, project_ids: Collection[UUID]
    ) -> MetadataRestoreResult:
        media = (
            MediaFileModel.objects.select_for_update()
            .filter(
                id=command.media_file_id,
                company_id=command.company_id,
                project_id__in=project_ids,
                archived_at__isnull=True,
            )
            .first()
        )
        if media is None:
            raise MediaFileNotFoundError
        if media.version != command.expected_version:
            raise MediaFileVersionConflictError
        target = MetadataVersionModel.objects.filter(
            media_file=media, version=command.target_version
        ).first()
        if target is None:
            raise MetadataVersionNotFoundError
        old_state = self._metadata_state(media)
        new_state = dict(target.snapshot)
        physical = FileVersionModel.objects.filter(media_file=media).order_by("sequence").first()
        if old_state == new_state:
            return MetadataRestoreResult(
                media_file=self._summary(media, physical),
                old_state=old_state,
                new_state=new_state,
                target_version=command.target_version,
                changed=False,
            )
        media.display_name = str(new_state["display_name"])
        media.description = str(new_state["description"])
        media.observations = str(new_state["observations"])
        recorded_at = new_state.get("recorded_at")
        media.recorded_at = parse_datetime(recorded_at) if recorded_at else None
        media.version += 1
        media.save(
            update_fields=[
                "display_name",
                "description",
                "observations",
                "recorded_at",
                "version",
                "updated_at",
            ]
        )
        MetadataVersionModel.objects.create(
            media_file=media,
            version=media.version,
            actor_user_id=command.actor_user_id,
            snapshot=new_state,
        )
        return MetadataRestoreResult(
            media_file=self._summary(media, physical),
            old_state=old_state,
            new_state=new_state,
            target_version=command.target_version,
            changed=True,
        )

    @staticmethod
    def _summary(media: MediaFileModel, physical: FileVersionModel) -> MediaFileSummary:
        return MediaFileSummary(
            id=media.id,
            project_id=media.project_id,
            original_name=media.original_name,
            display_name=media.display_name,
            media_type=media.media_type,
            description=media.description,
            observations=media.observations,
            size_bytes=physical.size_bytes,
            file_version_id=physical.id,
            source_machine_id=physical.source_machine_id,
            checksum_algorithm=physical.checksum_algorithm,
            checksum_digest=physical.checksum_digest,
            recorded_at=media.recorded_at,
            status=media.status,
            version=media.version,
            tags=tuple(
                TagSummary(
                    id=assignment.tag.id,
                    name=assignment.tag.name,
                    is_system=assignment.tag.is_system,
                )
                for assignment in media.tag_assignments.all()
                if assignment.tag.archived_at is None
            ),
        )

    @staticmethod
    def _metadata_state(media: MediaFileModel) -> dict[str, object]:
        return {
            "display_name": media.display_name,
            "description": media.description,
            "observations": media.observations,
            "recorded_at": media.recorded_at.isoformat() if media.recorded_at else None,
        }
