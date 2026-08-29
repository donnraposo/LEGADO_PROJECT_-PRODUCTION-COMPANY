import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("catalog", "0005_fileversion_ingestion_id"),
        ("companies", "0002_invitationmodel"),
        ("drive", "0003_drive_account_history"),
        ("operations", "0002_agent_command_execution"),
        ("projects", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="UploadBatchModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_by_user_id", models.UUIDField(db_index=True)),
                ("folder_date", models.DateField()),
                ("idempotency_key", models.CharField(max_length=120)),
                ("payload_digest", models.CharField(max_length=64)),
                ("status", models.CharField(db_index=True, default="CREATED", max_length=24)),
                ("total_items", models.PositiveIntegerField()),
                ("total_bytes", models.PositiveBigIntegerField()),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="companies.companymodel"
                    ),
                ),
                (
                    "drive_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="drive.driveaccountmodel"
                    ),
                ),
                (
                    "machine",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="operations.machinemodel"
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="projects.projectmodel"
                    ),
                ),
            ],
            options={"db_table": "upload_batches", "ordering": ["-created_at", "-id"]},
        ),
        migrations.CreateModel(
            name="UploadItemModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("destination_category", models.CharField(max_length=16)),
                ("final_name", models.CharField(max_length=255)),
                ("size_bytes", models.PositiveBigIntegerField()),
                ("checksum_algorithm", models.CharField(max_length=24)),
                ("checksum_digest", models.CharField(max_length=128)),
                ("position", models.PositiveIntegerField()),
                ("status", models.CharField(db_index=True, default="PENDING", max_length=24)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "batch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="items",
                        to="uploads.uploadbatchmodel",
                    ),
                ),
                (
                    "destination_folder",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="drive.drivefoldermodel"
                    ),
                ),
                (
                    "file_version",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="catalog.fileversionmodel"
                    ),
                ),
            ],
            options={"db_table": "upload_items", "ordering": ["position", "id"]},
        ),
        migrations.CreateModel(
            name="UploadAttemptModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("sequence", models.PositiveIntegerField()),
                ("status", models.CharField(db_index=True, default="CREATED", max_length=24)),
                ("session_reference_ciphertext", models.BinaryField(blank=True, default=bytes)),
                ("failure_code", models.CharField(blank=True, max_length=80)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="attempts",
                        to="uploads.uploaditemmodel",
                    ),
                ),
            ],
            options={"db_table": "upload_attempts", "ordering": ["sequence"]},
        ),
        migrations.CreateModel(
            name="UploadCheckpointModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("sequence", models.PositiveIntegerField()),
                ("confirmed_bytes", models.PositiveBigIntegerField()),
                ("source", models.CharField(default="DRIVE", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "attempt",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="checkpoints",
                        to="uploads.uploadattemptmodel",
                    ),
                ),
            ],
            options={"db_table": "upload_checkpoints", "ordering": ["sequence"]},
        ),
        migrations.AddConstraint(
            model_name="uploadbatchmodel",
            constraint=models.UniqueConstraint(
                fields=("company", "idempotency_key"), name="uq_upload_batch_idempotency"
            ),
        ),
        migrations.AddConstraint(
            model_name="uploadbatchmodel",
            constraint=models.CheckConstraint(
                condition=models.Q(("total_items__gte", 1), ("total_items__lte", 10000)),
                name="ck_upload_batch_item_count",
            ),
        ),
        migrations.AddConstraint(
            model_name="uploaditemmodel",
            constraint=models.UniqueConstraint(
                fields=("batch", "file_version"), name="uq_upload_item_batch_file_version"
            ),
        ),
        migrations.AddConstraint(
            model_name="uploaditemmodel",
            constraint=models.UniqueConstraint(
                fields=("batch", "position"), name="uq_upload_item_position"
            ),
        ),
        migrations.AddConstraint(
            model_name="uploaditemmodel",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ("status__in", ["PENDING", "READY", "UPLOADING", "VERIFYING", "PAUSED"])
                ),
                fields=("file_version",),
                name="uq_upload_item_active_file_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="uploaditemmodel",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("destination_category__in", ["ORIGINAIS", "PREVIEWS", "ENTREGAS"])
                ),
                name="ck_upload_item_category",
            ),
        ),
        migrations.AddConstraint(
            model_name="uploadattemptmodel",
            constraint=models.UniqueConstraint(
                fields=("item", "sequence"), name="uq_upload_attempt_sequence"
            ),
        ),
        migrations.AddConstraint(
            model_name="uploadattemptmodel",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status__in", ["CREATED", "ACTIVE", "INTERRUPTED"])),
                fields=("item",),
                name="uq_upload_attempt_active_item",
            ),
        ),
        migrations.AddConstraint(
            model_name="uploadcheckpointmodel",
            constraint=models.UniqueConstraint(
                fields=("attempt", "sequence"), name="uq_upload_checkpoint_sequence"
            ),
        ),
    ]
