from io import BytesIO
from unittest.mock import Mock, call, patch

from asgiref.sync import async_to_sync
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from modules.audit.infrastructure.persistence.models.audit_event_model import AuditEventModel
from modules.catalog.infrastructure.persistence.models.drive_object_model import DriveObjectModel
from modules.catalog.infrastructure.persistence.models.file_version_model import FileVersionModel
from modules.catalog.infrastructure.persistence.models.media_file_model import MediaFileModel
from modules.catalog.infrastructure.persistence.models.media_file_tag_model import (
    MediaFileTagModel,
)
from modules.catalog.infrastructure.persistence.models.metadata_version_model import (
    MetadataVersionModel,
)
from modules.catalog.infrastructure.persistence.models.tag_model import TagModel
from modules.companies.infrastructure.persistence.models.company_model import CompanyModel
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel
from modules.drive.infrastructure.persistence.models.drive_account_model import DriveAccountModel
from modules.identity.adapters.api.authenticated_principal import AuthenticatedPrincipal
from modules.identity.infrastructure.persistence.models.user_projection_model import (
    UserProjectionModel,
)
from modules.projects.infrastructure.persistence.models.client_model import ClientModel
from modules.projects.infrastructure.persistence.models.project_access_model import (
    ProjectAccessModel,
)
from modules.projects.infrastructure.persistence.models.project_model import ProjectModel


class MediaFileCollectionTest(TestCase):
    def setUp(self) -> None:
        self.owner = self._user("owner", "a")
        self.admin = self._user("admin", "b")
        self.company = CompanyModel.objects.create(name="Legado")
        MembershipModel.objects.create(
            company=self.company, user=self.owner, role="OWNER", status="ACTIVE"
        )
        MembershipModel.objects.create(
            company=self.company, user=self.admin, role="ADMINISTRATOR", status="ACTIVE"
        )
        client = ClientModel.objects.create(
            company=self.company, name="Cliente", normalized_name="cliente"
        )
        self.allowed_project = self._project(client, "Permitido")
        self.restricted_project = self._project(client, "Restrito")
        ProjectAccessModel.objects.create(project=self.allowed_project, user=self.admin)

    @staticmethod
    def _user(subject: str, prefix: str) -> UserProjectionModel:
        return UserProjectionModel.objects.create(
            keycloak_subject=subject,
            email_ciphertext=b"x",
            email_lookup_hmac=prefix * 64,
        )

    def _project(self, client: ClientModel, name: str) -> ProjectModel:
        return ProjectModel.objects.create(
            company=self.company,
            client=client,
            name=name,
            normalized_name=name.casefold(),
            created_by_user=self.owner,
        )

    def _api(self, user: UserProjectionModel) -> APIClient:
        client = APIClient()
        client.force_authenticate(user=AuthenticatedPrincipal(id=user.id))
        client.credentials(HTTP_X_COMPANY_ID=str(self.company.id))
        return client

    @staticmethod
    def _payload(project_id) -> dict[str, object]:
        return {
            "project_id": str(project_id),
            "original_name": r"D:\camera\clip.mov",
            "media_type": "video/quicktime",
            "size_bytes": 4096,
            "checksum_algorithm": "sha256",
            "checksum_digest": "a" * 64,
        }

    def test_owner_catalogs_file_without_persisting_local_path(self) -> None:
        response = self._api(self.owner).post(
            "/api/v1/media-files", self._payload(self.restricted_project.id), format="json"
        )

        assert response.status_code == 201
        assert response.json()["original_name"] == "clip.mov"
        assert MediaFileModel.objects.get().original_name == "clip.mov"
        assert FileVersionModel.objects.get().size_bytes == 4096

    def test_administrator_only_sees_and_creates_in_allowed_projects(self) -> None:
        owner_api = self._api(self.owner)
        owner_api.post("/api/v1/media-files", self._payload(self.allowed_project.id), format="json")
        owner_api.post(
            "/api/v1/media-files", self._payload(self.restricted_project.id), format="json"
        )

        admin_api = self._api(self.admin)
        listed = admin_api.get("/api/v1/media-files")
        denied = admin_api.post(
            "/api/v1/media-files", self._payload(self.restricted_project.id), format="json"
        )

        assert listed.status_code == 200
        assert len(listed.json()["items"]) == 1
        assert listed.json()["items"][0]["project_id"] == str(self.allowed_project.id)
        assert denied.status_code == 403

    def test_metadata_update_rejects_stale_version(self) -> None:
        api = self._api(self.owner)
        created = api.post(
            "/api/v1/media-files", self._payload(self.allowed_project.id), format="json"
        ).json()
        endpoint = f"/api/v1/media-files/{created['id']}"

        updated = api.patch(
            endpoint,
            {"display_name": "Corte final.mov", "expected_version": 1},
            format="json",
        )
        stale = api.patch(
            endpoint,
            {"description": "Versão antiga", "expected_version": 1},
            format="json",
        )

        assert updated.status_code == 200
        assert updated.json()["display_name"] == "Corte final.mov"
        assert updated.json()["version"] == 2
        assert stale.status_code == 409
        assert list(
            MetadataVersionModel.objects.order_by("version").values_list("version", flat=True)
        ) == [1, 2]
        history = MetadataVersionModel.objects.get(version=2)
        assert history.snapshot["display_name"] == "Corte final.mov"
        event = AuditEventModel.objects.get(event_type="MEDIA_METADATA_UPDATED")
        assert event.change_state == {"display_name": {"old": "clip.mov", "new": "Corte final.mov"}}

    def test_owner_creates_and_assigns_custom_tag(self) -> None:
        api = self._api(self.owner)
        media = api.post(
            "/api/v1/media-files", self._payload(self.allowed_project.id), format="json"
        ).json()

        created = api.post("/api/v1/tags", {"name": "  Making   of  "}, format="json")
        assigned = api.put(
            f"/api/v1/media-files/{media['id']}/tags/{created.json()['id']}"
        )

        assert created.status_code == 201
        assert created.json() == {
            "id": str(TagModel.objects.get(is_system=False).id),
            "name": "Making of",
            "is_system": False,
        }
        assert assigned.status_code == 204
        assert MediaFileTagModel.objects.filter(media_file_id=media["id"]).exists()

    def test_admin_cannot_create_tag_and_cannot_tag_restricted_media(self) -> None:
        owner_api = self._api(self.owner)
        media = owner_api.post(
            "/api/v1/media-files", self._payload(self.restricted_project.id), format="json"
        ).json()
        system_tag = TagModel.objects.get(normalized_name="aprovado", is_system=True)
        admin_api = self._api(self.admin)

        create_denied = admin_api.post("/api/v1/tags", {"name": "Interna"}, format="json")
        assignment_denied = admin_api.put(
            f"/api/v1/media-files/{media['id']}/tags/{system_tag.id}"
        )

        assert create_denied.status_code == 403
        assert assignment_denied.status_code == 404

    def test_owner_archives_only_custom_tags(self) -> None:
        api = self._api(self.owner)
        custom = api.post("/api/v1/tags", {"name": "Temporária"}, format="json").json()
        system_tag = TagModel.objects.get(normalized_name="final", is_system=True)

        archived = api.delete(f"/api/v1/tags/{custom['id']}")
        protected = api.delete(f"/api/v1/tags/{system_tag.id}")

        assert archived.status_code == 204
        assert protected.status_code == 404
        listed_names = {item["name"] for item in api.get("/api/v1/tags").json()["items"]}
        assert "Temporária" not in listed_names
        assert "Final" in listed_names

    def test_catalog_search_filters_and_cursor(self) -> None:
        api = self._api(self.owner)
        first = api.post(
            "/api/v1/media-files", self._payload(self.allowed_project.id), format="json"
        ).json()
        second_payload = self._payload(self.allowed_project.id)
        second_payload["original_name"] = "entrevista.mp4"
        second = api.post("/api/v1/media-files", second_payload, format="json").json()
        tag = TagModel.objects.get(normalized_name="selecionado", is_system=True)
        api.put(f"/api/v1/media-files/{second['id']}/tags/{tag.id}")

        searched = api.get("/api/v1/media-files", {"q": "entrevista"})
        tagged = api.get("/api/v1/media-files", {"tag_id": str(tag.id)})
        page_one = api.get("/api/v1/media-files", {"limit": 1}).json()
        page_two = api.get(
            "/api/v1/media-files", {"limit": 1, "cursor": page_one["next_cursor"]}
        ).json()

        assert [item["id"] for item in searched.json()["items"]] == [second["id"]]
        assert [item["id"] for item in tagged.json()["items"]] == [second["id"]]
        assert page_one["next_cursor"] is not None
        assert {page_one["items"][0]["id"], page_two["items"][0]["id"]} == {
            first["id"],
            second["id"],
        }
        assert page_two["next_cursor"] is None
        assert api.get("/api/v1/media-files", {"cursor": "inválido"}).status_code == 400

    def test_tag_changes_are_idempotent_audited_and_returned(self) -> None:
        api = self._api(self.owner)
        media = api.post(
            "/api/v1/media-files", self._payload(self.allowed_project.id), format="json"
        ).json()
        tag = TagModel.objects.get(normalized_name="selecionado", is_system=True)
        endpoint = f"/api/v1/media-files/{media['id']}/tags/{tag.id}"

        assert api.put(endpoint).status_code == 204
        assert api.put(endpoint).status_code == 204
        listed = api.get("/api/v1/media-files").json()["items"][0]
        assert listed["tags"] == [
            {"id": str(tag.id), "name": "Selecionado", "is_system": True}
        ]
        assert api.delete(endpoint).status_code == 204
        assert api.delete(endpoint).status_code == 204
        assert AuditEventModel.objects.filter(event_type="MEDIA_FILE_TAG_ASSIGNED").count() == 1
        assert AuditEventModel.objects.filter(event_type="MEDIA_FILE_TAG_REMOVED").count() == 1

    def test_metadata_history_and_owner_restore_create_new_version(self) -> None:
        api = self._api(self.owner)
        media = api.post(
            "/api/v1/media-files", self._payload(self.allowed_project.id), format="json"
        ).json()
        detail = f"/api/v1/media-files/{media['id']}"
        api.patch(
            detail,
            {"display_name": "Editado.mov", "expected_version": 1},
            format="json",
        )
        history_url = f"{detail}/metadata-history"

        history = api.get(history_url)
        first_page = api.get(history_url, {"limit": 1}).json()
        restored = api.post(
            f"{history_url}/1/restore", {"expected_version": 2}, format="json"
        )

        assert history.status_code == 200
        assert [item["version"] for item in history.json()["items"]] == [1, 2]
        assert first_page["next_version"] == 1
        assert [
            item["version"]
            for item in api.get(
                history_url, {"limit": 1, "after_version": first_page["next_version"]}
            ).json()["items"]
        ] == [2]
        assert restored.status_code == 200
        assert restored.json()["display_name"] == "clip.mov"
        assert restored.json()["version"] == 3
        assert list(
            MetadataVersionModel.objects.filter(media_file_id=media["id"])
            .order_by("version")
            .values_list("version", flat=True)
        ) == [1, 2, 3]
        assert AuditEventModel.objects.filter(event_type="MEDIA_METADATA_RESTORED").count() == 1

    def test_administrator_reads_history_but_cannot_restore(self) -> None:
        owner_api = self._api(self.owner)
        media = owner_api.post(
            "/api/v1/media-files", self._payload(self.allowed_project.id), format="json"
        ).json()
        history_url = f"/api/v1/media-files/{media['id']}/metadata-history"
        admin_api = self._api(self.admin)

        assert admin_api.get(history_url).status_code == 200
        assert (
            admin_api.post(
                f"{history_url}/1/restore", {"expected_version": 1}, format="json"
            ).status_code
            == 403
        )

    def test_catalog_combines_technical_filters(self) -> None:
        api = self._api(self.owner)
        first = api.post(
            "/api/v1/media-files", self._payload(self.allowed_project.id), format="json"
        ).json()
        second_payload = self._payload(self.allowed_project.id)
        second_payload.update(
            {
                "original_name": "foto.raw",
                "media_type": "image/x-raw",
                "size_bytes": 8192,
                "recorded_at": "2026-08-18T12:00:00Z",
            }
        )
        api.post("/api/v1/media-files", second_payload, format="json")

        filtered = api.get(
            "/api/v1/media-files",
            {
                "extension": ".mov",
                "media_type": "video/quicktime",
                "min_size_bytes": 4000,
                "max_size_bytes": 5000,
                "created_by_user_id": str(self.owner.id),
            },
        )

        assert filtered.status_code == 200
        assert [item["id"] for item in filtered.json()["items"]] == [first["id"]]
        assert (
            api.get(
                "/api/v1/media-files",
                {"min_size_bytes": 2, "max_size_bytes": 1},
            ).status_code
            == 400
        )

    @override_settings(
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
    )
    def test_playback_ticket_returns_stream_and_drive_fallback_for_authorized_file(self) -> None:
        created = self._api(self.owner).post(
            "/api/v1/media-files", self._payload(self.allowed_project.id), format="json"
        ).json()
        account = DriveAccountModel.objects.create(
            company=self.company,
            connected_by=self.owner,
            provider_account_id="drive-account",
            email_ciphertext=b"encrypted-email",
            refresh_token_ciphertext=b"encrypted-token",
            connected_at=timezone.now(),
        )
        DriveObjectModel.objects.create(
            file_version_id=created["file_version_id"],
            account=account,
            external_id="drive-file-123",
            object_reference="drive-file-123",
            status="CONFIRMED",
            name="clip.mov",
            size_bytes=4096,
            mime_type="video/quicktime",
        )

        response = self._api(self.owner).post(
            f"/api/v1/media-files/{created['id']}/playback"
        )

        assert response.status_code == 201
        assert response.json()["stream_url"].startswith("/api/v1/media-playback/")
        assert response.json()["download_url"].startswith("/api/v1/media-download/")
        assert response.json()["drive_url"] == (
            "https://drive.google.com/file/d/drive-file-123/view"
        )
        assert response.json()["expires_in"] == 600

    @override_settings(
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
    )
    def test_playback_ticket_hides_restricted_file_from_administrator(self) -> None:
        created = self._api(self.owner).post(
            "/api/v1/media-files", self._payload(self.restricted_project.id), format="json"
        ).json()
        account = DriveAccountModel.objects.create(
            company=self.company,
            connected_by=self.owner,
            provider_account_id="drive-account",
            email_ciphertext=b"encrypted-email",
            refresh_token_ciphertext=b"encrypted-token",
            connected_at=timezone.now(),
        )
        DriveObjectModel.objects.create(
            file_version_id=created["file_version_id"],
            account=account,
            external_id="restricted-file",
            status="CONFIRMED",
            name="restricted.mov",
        )

        response = self._api(self.admin).post(
            f"/api/v1/media-files/{created['id']}/playback"
        )

        assert response.status_code == 404

    @override_settings(
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
    )
    def test_playback_stream_forwards_range_and_returns_partial_content(self) -> None:
        created = self._api(self.owner).post(
            "/api/v1/media-files", self._payload(self.allowed_project.id), format="json"
        ).json()
        account = DriveAccountModel.objects.create(
            company=self.company,
            connected_by=self.owner,
            provider_account_id="drive-account",
            email_ciphertext=b"encrypted-email",
            refresh_token_ciphertext=b"encrypted-token",
            connected_at=timezone.now(),
        )
        drive_object = DriveObjectModel.objects.create(
            file_version_id=created["file_version_id"],
            account=account,
            external_id="drive-file-123",
            status="CONFIRMED",
            name="clip.mp4",
            mime_type="video/mp4",
        )
        cache.set("media-playback:test-ticket", {"drive_object_id": str(drive_object.id)}, 60)
        upstream = BytesIO(b"video-bytes")
        upstream.status = 206
        upstream.headers = {
            "Content-Type": "video/mp4",
            "Content-Length": "11",
            "Content-Range": "bytes 0-10/100",
            "Accept-Ranges": "bytes",
        }
        download_upstream = BytesIO(b"download-bytes")
        download_upstream.status = 200
        download_upstream.headers = {
            "Content-Type": "video/mp4",
            "Content-Length": "14",
        }
        protector = Mock()
        protector.decrypt.return_value = "refresh-token"
        oauth = Mock()
        oauth.refresh_access_token.return_value = "access-token"
        drive = Mock()
        drive.open_media.side_effect = [upstream, download_upstream]

        with (
            patch(
                "modules.catalog.adapters.api.media_playback_view.create_personal_data_protector",
                return_value=protector,
            ),
            patch(
                "modules.catalog.adapters.api.media_playback_view.create_google_oauth_gateway",
                return_value=oauth,
            ),
            patch(
                "modules.catalog.adapters.api.media_playback_view.create_google_drive_gateway",
                return_value=drive,
            ),
        ):
            response = APIClient().get(
                "/api/v1/media-playback/test-ticket", HTTP_RANGE="bytes=0-10"
            )

            async def consume_stream() -> bytes:
                chunks = [chunk async for chunk in response.streaming_content]
                return b"".join(chunks)

            content = async_to_sync(consume_stream)()

            download_response = APIClient().get("/api/v1/media-download/test-ticket")

            async def consume_download() -> bytes:
                chunks = [chunk async for chunk in download_response.streaming_content]
                return b"".join(chunks)

            download_content = async_to_sync(consume_download)()

        assert response.status_code == 206
        assert content == b"video-bytes"
        assert response["Content-Range"] == "bytes 0-10/100"
        assert response["Accept-Ranges"] == "bytes"
        assert download_content == b"download-bytes"
        assert download_response["Content-Disposition"] == (
            "attachment; filename*=UTF-8''clip.mp4"
        )
        assert drive.open_media.call_args_list == [
            call("access-token", "drive-file-123", "bytes=0-10"),
            call("access-token", "drive-file-123", ""),
        ]
