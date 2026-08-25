import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("companies", "0002_invitationmodel"),
        ("identity", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="DriveOAuthStateModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("state_digest", models.CharField(max_length=64, unique=True)),
                ("expires_at", models.DateTimeField()),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "actor_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="identity.userprojectionmodel",
                    ),
                ),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="companies.companymodel"
                    ),
                ),
            ],
            options={"db_table": "drive_oauth_states"},
        ),
        migrations.CreateModel(
            name="DriveAccountModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("provider_account_id", models.CharField(max_length=255)),
                ("email_ciphertext", models.BinaryField()),
                ("refresh_token_ciphertext", models.BinaryField()),
                ("granted_scopes", models.TextField(default="")),
                ("connected_at", models.DateTimeField()),
                ("disconnected_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="drive_account",
                        to="companies.companymodel",
                    ),
                ),
                (
                    "connected_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="connected_drive_accounts",
                        to="identity.userprojectionmodel",
                    ),
                ),
            ],
            options={"db_table": "drive_accounts"},
        ),
        migrations.AddIndex(
            model_name="driveoauthstatemodel",
            index=models.Index(fields=["expires_at"], name="drive_oauth_expires_dd5ac8_idx"),
        ),
    ]
