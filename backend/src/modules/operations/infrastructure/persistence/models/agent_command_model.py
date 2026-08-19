import uuid

from django.db import models


class AgentCommandModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.UUIDField(db_index=True)
    machine = models.ForeignKey(
        "operations.MachineModel", on_delete=models.PROTECT, related_name="commands"
    )
    created_by_user_id = models.UUIDField(db_index=True)
    command_type = models.CharField(max_length=60)
    resource_type = models.CharField(max_length=60)
    resource_id = models.UUIDField(null=True, blank=True)
    payload = models.JSONField(default=dict)
    payload_digest = models.CharField(max_length=64)
    idempotency_key = models.CharField(max_length=120)
    sequence = models.PositiveBigIntegerField()
    correlation_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    status = models.CharField(max_length=20, default="PENDING", db_index=True)
    progress_percent = models.PositiveSmallIntegerField(default=0)
    result = models.JSONField(default=dict)
    failure_code = models.CharField(max_length=80, blank=True)
    version = models.PositiveBigIntegerField(default=1)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "agent_commands"
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "idempotency_key"],
                name="uq_agent_command_idempotency",
            ),
            models.UniqueConstraint(
                fields=["machine", "sequence"], name="uq_agent_command_machine_sequence"
            ),
        ]
