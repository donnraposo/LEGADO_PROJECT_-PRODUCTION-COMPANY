from modules.catalog.application.exceptions import InvalidMediaFileTransitionError
from modules.catalog.domain.media_file_status import MediaFileStatus


class MediaFileTransitionPolicy:
    _ALLOWED = {
        MediaFileStatus.DISCOVERED: {MediaFileStatus.ANALYZED, MediaFileStatus.CANCELLED},
        MediaFileStatus.ANALYZED: {
            MediaFileStatus.AWAITING_CONFIRMATION,
            MediaFileStatus.CONFLICT,
            MediaFileStatus.CANCELLED,
        },
        MediaFileStatus.AWAITING_CONFIRMATION: {
            MediaFileStatus.ORGANIZING,
            MediaFileStatus.CANCELLED,
        },
        MediaFileStatus.ORGANIZING: {
            MediaFileStatus.ORGANIZED,
            MediaFileStatus.INTERRUPTED,
            MediaFileStatus.DEVICE_DISCONNECTED,
            MediaFileStatus.CONFLICT,
        },
        MediaFileStatus.ORGANIZED: {MediaFileStatus.AWAITING_UPLOAD},
        MediaFileStatus.AWAITING_UPLOAD: {
            MediaFileStatus.UPLOADING,
            MediaFileStatus.AWAITING_INTERNET,
            MediaFileStatus.CANCELLED,
        },
        MediaFileStatus.UPLOADING: {
            MediaFileStatus.VERIFYING,
            MediaFileStatus.AWAITING_INTERNET,
            MediaFileStatus.DEVICE_DISCONNECTED,
            MediaFileStatus.INTERRUPTED,
            MediaFileStatus.AWAITING_INTERVENTION,
            MediaFileStatus.CANCELLED,
        },
        MediaFileStatus.VERIFYING: {
            MediaFileStatus.SYNCHRONIZED,
            MediaFileStatus.INTEGRITY_FAILURE,
            MediaFileStatus.AWAITING_INTERVENTION,
        },
        MediaFileStatus.CONFLICT: {
            MediaFileStatus.AWAITING_CONFIRMATION,
            MediaFileStatus.CANCELLED,
        },
        MediaFileStatus.INTERRUPTED: {
            MediaFileStatus.ANALYZED,
            MediaFileStatus.AWAITING_UPLOAD,
            MediaFileStatus.UPLOADING,
            MediaFileStatus.CANCELLED,
        },
        MediaFileStatus.AWAITING_INTERNET: {
            MediaFileStatus.UPLOADING,
            MediaFileStatus.CANCELLED,
        },
        MediaFileStatus.DEVICE_DISCONNECTED: {
            MediaFileStatus.ANALYZED,
            MediaFileStatus.UPLOADING,
            MediaFileStatus.CANCELLED,
        },
        MediaFileStatus.INTEGRITY_FAILURE: {
            MediaFileStatus.AWAITING_INTERVENTION,
            MediaFileStatus.CANCELLED,
        },
        MediaFileStatus.AWAITING_INTERVENTION: {
            MediaFileStatus.ANALYZED,
            MediaFileStatus.AWAITING_UPLOAD,
            MediaFileStatus.UPLOADING,
            MediaFileStatus.CANCELLED,
        },
        MediaFileStatus.SYNCHRONIZED: set(),
        MediaFileStatus.CANCELLED: set(),
    }

    @classmethod
    def validate(cls, current: str, target: str) -> None:
        try:
            current_status = MediaFileStatus(current)
            target_status = MediaFileStatus(target)
        except ValueError as exc:
            raise InvalidMediaFileTransitionError from exc
        if target_status not in cls._ALLOWED[current_status]:
            raise InvalidMediaFileTransitionError
