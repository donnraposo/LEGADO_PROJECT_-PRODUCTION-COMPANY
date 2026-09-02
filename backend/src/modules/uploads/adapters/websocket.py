from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.cache import cache

from modules.companies.infrastructure.persistence.models.membership_model import MembershipModel
from modules.uploads.infrastructure.upload_events import upload_company_group


class UploadConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        ticket = self.scope["url_route"]["kwargs"]["ticket"]
        ticket_key = f"upload-ws-ticket:{ticket}"
        identity = await cache.aget(ticket_key)
        await cache.adelete(ticket_key)
        if not identity or not await self._membership_is_active(identity):
            await self.close(code=4401)
            return
        self.identity = identity
        self.group_name = upload_company_group(identity["company_id"])
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json({"type": "connected"})

    async def disconnect(self, _code) -> None:
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def upload_changed(self, event) -> None:
        if not await self._membership_is_active(self.identity):
            await self.close(code=4403)
            return
        await self.send_json({"type": "upload.changed", "batch_id": event["batch_id"]})

    @database_sync_to_async
    def _membership_is_active(self, identity: dict) -> bool:
        return MembershipModel.objects.filter(
            company_id=identity["company_id"],
            user_id=identity["user_id"],
            status="ACTIVE",
        ).exists()
