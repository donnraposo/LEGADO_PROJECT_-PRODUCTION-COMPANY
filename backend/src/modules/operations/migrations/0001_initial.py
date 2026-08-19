import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MachineModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("company_id", models.UUIDField(db_index=True)),
                ("installation_id", models.UUIDField()),
                ("registered_by_user_id", models.UUIDField(db_index=True)),
                ("display_name", models.CharField(max_length=120)),
                ("os_family", models.CharField(max_length=40)),
                ("agent_version", models.CharField(max_length=40)),
                ("status", models.CharField(db_index=True, default="ONLINE", max_length=20)),
                ("last_seen_at", models.DateTimeField()),
                ("command_sequence", models.PositiveBigIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "machines",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("company_id", "installation_id"),
                        name="uq_machine_company_installation",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="AgentCommandModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("company_id", models.UUIDField(db_index=True)),
                ("created_by_user_id", models.UUIDField(db_index=True)),
                ("command_type", models.CharField(max_length=60)),
                ("resource_type", models.CharField(max_length=60)),
                ("resource_id", models.UUIDField(blank=True, null=True)),
                ("payload", models.JSONField(default=dict)),
                ("payload_digest", models.CharField(max_length=64)),
                ("idempotency_key", models.CharField(max_length=120)),
                ("sequence", models.PositiveBigIntegerField()),
                ("correlation_id", models.UUIDField(db_index=True, default=uuid.uuid4)),
                ("status", models.CharField(db_index=True, default="PENDING", max_length=20)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "machine",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="commands",
                        to="operations.machinemodel",
                    ),
                ),
            ],
            options={
                "db_table": "agent_commands",
                "ordering": ["sequence"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("company_id", "idempotency_key"),
                        name="uq_agent_command_idempotency",
                    ),
                    models.UniqueConstraint(
                        fields=("machine", "sequence"),
                        name="uq_agent_command_machine_sequence",
                    ),
                ],
            },
        ),
    ]
