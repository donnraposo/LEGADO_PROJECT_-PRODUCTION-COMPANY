import uuid

from django.db import models
from django.db.models import Q


class TagModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.UUIDField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=80)
    normalized_name = models.CharField(max_length=80)
    is_system = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tags"
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["normalized_name"],
                condition=Q(is_system=True),
                name="uq_system_tag_name",
            ),
            models.UniqueConstraint(
                fields=["company_id", "normalized_name"],
                condition=Q(is_system=False),
                name="uq_company_tag_name",
            ),
        ]
