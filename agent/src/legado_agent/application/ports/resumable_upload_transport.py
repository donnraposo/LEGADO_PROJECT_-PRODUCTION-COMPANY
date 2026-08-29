from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChunkUploadResult:
    confirmed_bytes: int
    completed: bool
    provider_object_id: str = ""


class SessionExpiredError(Exception):
    pass


class UploadTransportError(Exception):
    code = "INTERNET_UNAVAILABLE"


class UploadAuthenticationError(UploadTransportError):
    code = "AUTHENTICATION_REQUIRED"


class UploadQuotaError(UploadTransportError):
    code = "DRIVE_QUOTA_EXCEEDED"


class ResumableUploadTransport(ABC):
    @abstractmethod
    def send_chunk(
        self,
        session_url: str,
        chunk: bytes,
        offset: int,
        total_bytes: int,
    ) -> ChunkUploadResult:
        raise NotImplementedError
