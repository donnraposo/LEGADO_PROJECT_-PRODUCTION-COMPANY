from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("operations", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="agentcommandmodel",
            name="acknowledged_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="agentcommandmodel",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="agentcommandmodel",
            name="failure_code",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="agentcommandmodel",
            name="progress_percent",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="agentcommandmodel",
            name="result",
            field=models.JSONField(default=dict),
        ),
    ]
