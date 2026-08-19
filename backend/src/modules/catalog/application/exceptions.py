class CatalogProjectAccessDeniedError(Exception):
    pass


class CatalogIngestionConflictError(Exception):
    pass


class CatalogIngestionRaceError(Exception):
    pass


class MediaFileNotFoundError(Exception):
    pass


class MediaFileVersionConflictError(Exception):
    pass


class TagManagementDeniedError(Exception):
    pass


class TagNotFoundError(Exception):
    pass


class TagNameConflictError(Exception):
    pass


class InvalidCatalogCursorError(Exception):
    pass


class InvalidMediaFileTransitionError(Exception):
    pass


class MachineCatalogAccessDeniedError(Exception):
    pass


class MetadataVersionNotFoundError(Exception):
    pass


class MetadataRestoreDeniedError(Exception):
    pass
