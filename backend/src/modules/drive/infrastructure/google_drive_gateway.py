import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from modules.drive.application.exceptions import GoogleOAuthExchangeError


@dataclass(frozen=True, slots=True)
class ResumableSessionState:
    status: str
    confirmed_bytes: int = 0


class GoogleDriveGateway:
    FILES_ENDPOINT = "https://www.googleapis.com/drive/v3/files"
    RESUMABLE_UPLOAD_ENDPOINT = (
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&fields=id"
    )
    FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"

    def create_resumable_session(
        self,
        access_token: str,
        parent_id: str,
        name: str,
        size_bytes: int,
        content_type: str,
    ) -> str:
        request = Request(
            self.RESUMABLE_UPLOAD_ENDPOINT,
            data=json.dumps({"name": name, "parents": [parent_id]}).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Length": str(size_bytes),
                "X-Upload-Content-Type": content_type,
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=20) as response:  # noqa: S310
                location = response.headers.get("Location")
        except (HTTPError, URLError, TimeoutError) as exc:
            raise GoogleOAuthExchangeError(
                "Não foi possível iniciar a sessão retomável no Google Drive."
            ) from exc
        if not location:
            raise GoogleOAuthExchangeError("O Google Drive não devolveu a sessão retomável.")
        return location

    def inspect_resumable_session(self, session_url: str, size_bytes: int) -> ResumableSessionState:
        request = Request(
            session_url,
            data=b"",
            headers={
                "Content-Length": "0",
                "Content-Range": f"bytes */{size_bytes}",
            },
            method="PUT",
        )
        try:
            with urlopen(request, timeout=20):  # noqa: S310
                return ResumableSessionState("COMPLETED", size_bytes)
        except HTTPError as exc:
            if exc.code == 308:
                return ResumableSessionState(
                    "ACTIVE", self._confirmed_bytes(exc.headers.get("Range", ""))
                )
            if exc.code in {404, 410}:
                return ResumableSessionState("EXPIRED")
            raise GoogleOAuthExchangeError(
                "Não foi possível consultar a sessão retomável no Google Drive."
            ) from exc
        except (URLError, TimeoutError) as exc:
            raise GoogleOAuthExchangeError(
                "Não foi possível consultar a sessão retomável no Google Drive."
            ) from exc

    @staticmethod
    def _confirmed_bytes(range_header: str) -> int:
        try:
            return int(range_header.rsplit("-", 1)[1]) + 1
        except IndexError, ValueError:
            return 0

    def ensure_folder(self, access_token: str, name: str, parent_id: str = "") -> str:
        escaped_name = name.replace("\\", "\\\\").replace("'", "\\'")
        query_parts = [
            f"name = '{escaped_name}'",
            f"mimeType = '{self.FOLDER_MIME_TYPE}'",
            "trashed = false",
        ]
        if parent_id:
            query_parts.append(f"'{parent_id}' in parents")
        query_string = urlencode(
            {"q": " and ".join(query_parts), "fields": "files(id)", "pageSize": 1}
        )
        result = self._request_json(
            Request(
                f"{self.FILES_ENDPOINT}?{query_string}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        )
        if result.get("files"):
            return result["files"][0]["id"]
        body: dict[str, object] = {"name": name, "mimeType": self.FOLDER_MIME_TYPE}
        if parent_id:
            body["parents"] = [parent_id]
        created = self._request_json(
            Request(
                f"{self.FILES_ENDPOINT}?fields={quote('id')}",
                data=json.dumps(body).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
        )
        return created["id"]

    def get_object(self, access_token: str, object_id: str) -> dict:
        fields = quote("id,name,size,sha256Checksum,md5Checksum,mimeType,parents,trashed")
        return self._request_json(
            Request(
                f"{self.FILES_ENDPOINT}/{quote(object_id)}?fields={fields}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        )

    def open_media(self, access_token: str, object_id: str, range_header: str = ""):
        headers = {"Authorization": f"Bearer {access_token}"}
        if range_header:
            headers["Range"] = range_header
        request = Request(
            f"{self.FILES_ENDPOINT}/{quote(object_id, safe='')}?alt=media",
            headers=headers,
        )
        try:
            return urlopen(request, timeout=20)  # noqa: S310
        except (HTTPError, URLError, TimeoutError) as exc:
            raise GoogleOAuthExchangeError(
                "Não foi possível reproduzir o arquivo do Google Drive."
            ) from exc

    @staticmethod
    def _request_json(request: Request) -> dict:
        try:
            with urlopen(request, timeout=20) as response:  # noqa: S310
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            try:
                payload = json.loads(exc.read().decode("utf-8"))
                error = payload.get("error", {})
                reason = (error.get("errors") or [{}])[0].get(
                    "reason", error.get("status", "HTTP_ERROR")
                )
            except json.JSONDecodeError, UnicodeDecodeError:
                reason = "HTTP_ERROR"
            raise GoogleOAuthExchangeError(
                f"Google Drive recusou a operação ({exc.code}, {reason})."
            ) from exc
        except (URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            raise GoogleOAuthExchangeError("Falha na comunicação com o Google Drive.") from exc
