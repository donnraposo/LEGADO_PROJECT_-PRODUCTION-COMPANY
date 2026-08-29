from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("uploads", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="uploadbatchmodel",
            name="last_control_action",
            field=models.CharField(blank=True, max_length=16),
        ),
        migrations.AddField(
            model_name="uploadbatchmodel",
            name="last_control_key",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="uploaditemmodel",
            name="last_control_action",
            field=models.CharField(blank=True, max_length=16),
        ),
        migrations.AddField(
            model_name="uploaditemmodel",
            name="last_control_key",
            field=models.CharField(blank=True, max_length=120),
        ),
    ]
