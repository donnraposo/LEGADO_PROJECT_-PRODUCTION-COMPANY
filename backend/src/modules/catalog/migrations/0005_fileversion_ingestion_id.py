from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalog", "0004_media_file_status_constraint")]

    operations = [
        migrations.AddField(
            model_name="fileversionmodel",
            name="ingestion_id",
            field=models.UUIDField(blank=True, null=True, unique=True),
        )
    ]
