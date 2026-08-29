import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("drive", "0001_initial"),
        ("projects", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="DriveFolderModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("folder_key", models.CharField(max_length=255)),
                ("provider_folder_id", models.CharField(max_length=255)),
                ("parent_provider_folder_id", models.CharField(blank=True, max_length=255)),
                ("name", models.CharField(max_length=160)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="folders",
                        to="drive.driveaccountmodel",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="drive_folders",
                        to="projects.projectmodel",
                    ),
                ),
            ],
            options={"db_table": "drive_folders"},
        ),
        migrations.AddConstraint(
            model_name="drivefoldermodel",
            constraint=models.UniqueConstraint(
                fields=("account", "folder_key"),
                name="uq_drive_folder_account_key",
            ),
        ),
    ]
