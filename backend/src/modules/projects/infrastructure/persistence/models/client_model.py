import uuid

from django.db import models


class ClientModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey("companies.CompanyModel", on_delete=models.PROTECT)
    name = models.CharField(max_length=160)
    normalized_name = models.CharField(max_length=160)
    archived_at = models.DateTimeField(null=True, blank=True)
    version = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clients"
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "normalized_name"], name="uq_client_company_name"
            )
        ]
