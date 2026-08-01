import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="AuditEventModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("company_id", models.UUIDField(db_index=True)),
                ("actor_user_id", models.UUIDField(db_index=True)),
                ("event_type", models.CharField(db_index=True, max_length=120)),
                ("subject_type", models.CharField(max_length=80)),
                ("subject_id", models.UUIDField()),
                ("before", models.JSONField(blank=True, null=True)),
                ("after", models.JSONField(blank=True, null=True)),
                ("correlation_id", models.UUIDField(db_index=True, default=uuid.uuid4)),
                ("occurred_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={"db_table": "audit_events", "ordering": ["-occurred_at", "id"]},
        )
    ]
