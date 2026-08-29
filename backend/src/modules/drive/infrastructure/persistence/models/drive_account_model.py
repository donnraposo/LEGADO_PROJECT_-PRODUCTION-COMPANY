import uuid

from django.db import models


class DriveAccountModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "companies.CompanyModel",
        on_delete=models.PROTECT,
        related_name="drive_accounts",
    )
    connected_by = models.ForeignKey(
        "identity.UserProjectionModel",
        on_delete=models.PROTECT,
        related_name="connected_drive_accounts",
    )
    provider_account_id = models.CharField(max_length=255)
    email_ciphertext = models.BinaryField()
    refresh_token_ciphertext = models.BinaryField()
    granted_scopes = models.TextField(default="")
    connected_at = models.DateTimeField()
    disconnected_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "drive_accounts"
        constraints = [
            models.UniqueConstraint(
                fields=["company"],
                condition=models.Q(disconnected_at__isnull=True),
                name="uq_drive_active_account_company",
            )
        ]
