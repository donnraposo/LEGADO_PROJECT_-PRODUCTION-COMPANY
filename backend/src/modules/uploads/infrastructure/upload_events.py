from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction


def upload_company_group(company_id) -> str:
    return f"uploads.company.{company_id}"


def publish_upload_change(company_id, batch_id) -> None:
    def send() -> None:
        layer = get_channel_layer()
        if layer is not None:
            async_to_sync(layer.group_send)(
                upload_company_group(company_id),
                {
                    "type": "upload.changed",
                    "batch_id": str(batch_id),
                },
            )

    transaction.on_commit(send)
