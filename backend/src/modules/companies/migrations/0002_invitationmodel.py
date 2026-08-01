import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("companies", "0001_initial"),
        ("identity", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="InvitationModel",
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
                ("email_ciphertext", models.BinaryField()),
                ("email_lookup_hmac", models.CharField(max_length=64)),
                ("token_digest", models.CharField(max_length=64, unique=True)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("OWNER", "OWNER"),
                            ("ADMINISTRATOR", "ADMINISTRATOR"),
                        ],
                        max_length=20,
                    ),
                ),
                ("expires_at", models.DateTimeField()),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                ("cancelled_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="invitations",
                        to="companies.companymodel",
                    ),
                ),
                (
                    "invited_by_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sent_company_invitations",
                        to="identity.userprojectionmodel",
                    ),
                ),
            ],
            options={
                "db_table": "company_invitations",
                "ordering": ["-created_at", "id"],
            },
        ),
    ]
