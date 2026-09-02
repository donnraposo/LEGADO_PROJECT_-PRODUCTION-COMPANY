from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.core.cache import cache
from django.test import TransactionTestCase, override_settings

from config.asgi import application
from modules.companies.infrastructure.persistence.models.company_model import CompanyModel
from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel
from modules.identity.infrastructure.persistence.models.user_projection_model import (
    UserProjectionModel,
)


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}},
)
class UploadWebsocketTest(TransactionTestCase):
    def setUp(self) -> None:
        self.user = UserProjectionModel.objects.create(
            keycloak_subject="websocket-owner",
            email_ciphertext=b"encrypted",
            email_lookup_hmac="w" * 64,
        )
        self.company = CompanyModel.objects.create(name="Produtora")
        MembershipModel.objects.create(company=self.company, user=self.user, role="OWNER")

    def test_ticket_is_single_use_and_revoked_membership_is_rejected(self) -> None:
        async_to_sync(self._exercise_connections)()

    async def _exercise_connections(self) -> None:
        identity = {"company_id": str(self.company.id), "user_id": str(self.user.id)}
        await cache.aset("upload-ws-ticket:valid", identity, timeout=60)
        first = WebsocketCommunicator(application, "/ws/uploads/valid")
        connected, _ = await first.connect()
        assert connected
        assert await first.receive_json_from() == {"type": "connected"}
        await self._block_membership()
        await get_channel_layer().group_send(
            f"uploads.company.{self.company.id}",
            {"type": "upload.changed", "batch_id": "batch-id"},
        )
        assert (await first.receive_output())["code"] == 4403

        reused = WebsocketCommunicator(application, "/ws/uploads/valid")
        connected, close_code = await reused.connect()
        assert not connected
        assert close_code == 4401

        await cache.aset("upload-ws-ticket:unknown", {}, timeout=60)
        unknown = WebsocketCommunicator(application, "/ws/uploads/unknown")
        connected, close_code = await unknown.connect()
        assert not connected
        assert close_code == 4401

    @database_sync_to_async
    def _block_membership(self) -> None:
        MembershipModel.objects.filter(company=self.company, user=self.user).update(
            status="BLOCKED"
        )
