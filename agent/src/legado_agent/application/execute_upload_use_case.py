from dataclasses import replace
from pathlib import Path
from uuid import UUID

from legado_agent.application.ports.backend_gateway import BackendGateway
from legado_agent.application.ports.checksum_calculator import ChecksumCalculator
from legado_agent.application.ports.resumable_upload_transport import (
    ResumableUploadTransport,
    SessionExpiredError,
    UploadTransportError,
)
from legado_agent.application.ports.upload_repository import UploadRepository
from legado_agent.domain.upload_job import UploadJob


class UploadFileError(Exception):
    pass


class ExecuteUploadUseCase:
    def __init__(
        self,
        repository: UploadRepository,
        backend: BackendGateway,
        transport: ResumableUploadTransport,
        checksum: ChecksumCalculator,
        chunk_size: int = 8 * 1024 * 1024,
    ) -> None:
        if chunk_size < 256 * 1024 or chunk_size % (256 * 1024):
            raise ValueError("O bloco deve ser múltiplo de 256 KiB.")
        self._repository = repository
        self._backend = backend
        self._transport = transport
        self._checksum = checksum
        self._chunk_size = chunk_size

    @property
    def repository(self) -> UploadRepository:
        return self._repository

    def execute(self, company_id: UUID, machine_id: UUID, item_id: UUID) -> UploadJob:
        session = self._backend.ensure_upload_session(company_id, machine_id, item_id)
        source_path = self._repository.source_path(session.media_file_id)
        if not source_path:
            raise UploadFileError("SOURCE_DISK_UNAVAILABLE")
        path = Path(source_path)
        if not path.is_file() or path.stat().st_size != session.size_bytes:
            raise UploadFileError("SOURCE_DISK_UNAVAILABLE")
        if self._checksum.calculate(path) != session.checksum_sha256.casefold():
            raise UploadFileError("INTEGRITY_MISMATCH")

        job = UploadJob(
            item_id=item_id,
            media_file_id=session.media_file_id,
            source_path=str(path),
            attempt_id=session.attempt_id,
            size_bytes=session.size_bytes,
            checksum_sha256=session.checksum_sha256,
            confirmed_bytes=session.confirmed_bytes,
            status="RUNNING",
        )
        self._repository.save(job)
        try:
            with path.open("rb") as stream:
                while job.confirmed_bytes < job.size_bytes:
                    control = self._backend.upload_control(company_id, machine_id, item_id)
                    if control in {"PAUSE_REQUESTED", "PAUSED"}:
                        job = replace(job, status="PAUSED")
                        self._repository.save(job)
                        if control == "PAUSE_REQUESTED":
                            self._backend.report_upload_state(
                                company_id, machine_id, item_id, "PAUSED", job.confirmed_bytes
                            )
                        return job
                    if control == "CANCEL_REQUESTED":
                        job = replace(job, status="CANCELLED")
                        self._repository.save(job)
                        self._backend.report_upload_state(
                            company_id, machine_id, item_id, "CANCELLED", job.confirmed_bytes
                        )
                        return job
                    stream.seek(job.confirmed_bytes)
                    chunk = stream.read(min(self._chunk_size, job.size_bytes - job.confirmed_bytes))
                    try:
                        result = self._transport.send_chunk(
                            session.session_url,
                            chunk,
                            job.confirmed_bytes,
                            job.size_bytes,
                        )
                    except SessionExpiredError:
                        session = self._backend.ensure_upload_session(
                            company_id, machine_id, item_id
                        )
                        job = replace(
                            job,
                            attempt_id=session.attempt_id,
                            confirmed_bytes=session.confirmed_bytes,
                        )
                        self._repository.save(job)
                        continue
                    if result.confirmed_bytes <= job.confirmed_bytes:
                        raise UploadTransportError("O Drive não confirmou avanço do upload.")
                    job = replace(
                        job,
                        confirmed_bytes=result.confirmed_bytes,
                        status="SUCCEEDED" if result.completed else "RUNNING",
                    )
                    self._repository.save(job)
                    self._backend.record_upload_checkpoint(
                        company_id, job.attempt_id, result.confirmed_bytes
                    )
                    if result.completed:
                        self._backend.confirm_upload_object(
                            company_id, machine_id, job.attempt_id, result.provider_object_id
                        )
            return job
        except (OSError, UploadTransportError) as exc:
            code = getattr(exc, "code", "SOURCE_DISK_UNAVAILABLE")
            job = replace(job, status="INTERRUPTED", error_code=code)
            self._repository.save(job)
            self._backend.report_upload_state(
                company_id, machine_id, item_id, "INTERRUPTED", job.confirmed_bytes, job.error_code
            )
            raise UploadFileError("O upload foi interrompido e poderá ser retomado.") from exc
