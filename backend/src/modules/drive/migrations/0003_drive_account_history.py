import django.db.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("drive", "0002_drivefoldermodel")]
    operations = [
        migrations.AlterField(
            model_name="driveaccountmodel",
            name="company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="drive_accounts",
                to="companies.companymodel",
            ),
        ),
        migrations.AddConstraint(
            model_name="driveaccountmodel",
            constraint=models.UniqueConstraint(
                condition=django.db.models.Q(("disconnected_at__isnull", True)),
                fields=("company",),
                name="uq_drive_active_account_company",
            ),
        ),
    ]
