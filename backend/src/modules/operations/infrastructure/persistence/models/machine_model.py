import uuid

from django.db import models


class MachineModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.UUIDField(db_index=True)
    installation_id = models.UUIDField()
    registered_by_user_id = models.UUIDField(db_index=True)
    display_name = models.CharField(max_length=120)
    os_family = models.CharField(max_length=40)
    agent_version = models.CharField(max_length=40)
    status = models.CharField(max_length=20, default="ONLINE", db_index=True)
    last_seen_at = models.DateTimeField()
    command_sequence = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "machines"
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "installation_id"],
                name="uq_machine_company_installation",
            )
        ]
