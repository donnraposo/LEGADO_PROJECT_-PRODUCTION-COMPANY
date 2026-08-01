import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="UserProjectionModel",
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
                ("keycloak_subject", models.CharField(max_length=255, unique=True)),
                ("email_ciphertext", models.BinaryField()),
                ("email_lookup_hmac", models.CharField(max_length=64, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "identity_users"},
        )
    ]
