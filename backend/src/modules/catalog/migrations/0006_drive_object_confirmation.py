import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0005_fileversion_ingestion_id"),
        ("drive", "0003_drive_account_history"),
        ("uploads", "0001_initial"),
    ]
    operations = [
        migrations.AddField(
            model_name="driveobjectmodel",
            name="account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="drive.driveaccountmodel",
            ),
        ),
        migrations.AddField(
            model_name="driveobjectmodel",
            name="folder",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="drive.drivefoldermodel",
            ),
        ),
        migrations.AddField(
            model_name="driveobjectmodel",
            name="upload_item",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="drive_object",
                to="uploads.uploaditemmodel",
            ),
        ),
        migrations.AddField(
            model_name="driveobjectmodel",
            name="name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="driveobjectmodel",
            name="size_bytes",
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="driveobjectmodel",
            name="checksum_sha256",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="driveobjectmodel",
            name="mime_type",
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AddConstraint(
            model_name="driveobjectmodel",
            constraint=models.UniqueConstraint(
                fields=("account", "external_id"), name="uq_drive_object_account_external"
            ),
        ),
    ]
