import httpx

from legado_agent.application.ports.resumable_upload_transport import (
    ChunkUploadResult,
    ResumableUploadTransport,
    SessionExpiredError,
    UploadAuthenticationError,
    UploadQuotaError,
    UploadTransportError,
)


class HttpResumableUploadTransport(ResumableUploadTransport):
    def __init__(self, timeout: float = 60.0, transport: httpx.BaseTransport | None = None) -> None:
        self._client = httpx.Client(timeout=timeout, transport=transport)

    def close(self) -> None:
        self._client.close()

    def send_chunk(
        self, session_url: str, chunk: bytes, offset: int, total_bytes: int
    ) -> ChunkUploadResult:
        end = offset + len(chunk) - 1
        try:
            response = self._client.put(
                session_url,
                content=chunk,
                headers={
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {offset}-{end}/{total_bytes}",
                },
            )
        except httpx.HTTPError as exc:
            raise UploadTransportError("Falha de comunicação com o Google Drive.") from exc
        if response.status_code in {404, 410}:
            raise SessionExpiredError
        if response.status_code == 401:
            raise UploadAuthenticationError("A autenticação do Google expirou.")
        if response.status_code == 403:
            reason = response.text.casefold()
            if "quota" in reason or "storagequota" in reason:
                raise UploadQuotaError("A cota do Google Drive foi atingida.")
            raise UploadAuthenticationError("O Google Drive recusou a autorização.")
        if response.status_code == 308:
            return ChunkUploadResult(
                self._confirmed_bytes(response.headers.get("Range", "")), False
            )
        if response.status_code in {200, 201}:
            try:
                object_id = str(response.json()["id"])
            except (KeyError, TypeError, ValueError) as exc:
                raise UploadTransportError(
                    "O Drive não devolveu o identificador do objeto."
                ) from exc
            return ChunkUploadResult(total_bytes, True, object_id)
        raise UploadTransportError(f"O Google Drive recusou o bloco ({response.status_code}).")

    @staticmethod
    def _confirmed_bytes(range_header: str) -> int:
        try:
            return int(range_header.rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            return 0
