import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("companies", "0001_initial"), ("identity", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="ClientModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=160)),
                ("normalized_name", models.CharField(max_length=160)),
                ("archived_at", models.DateTimeField(blank=True, null=True)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="companies.companymodel"
                    ),
                ),
            ],
            options={"db_table": "clients", "ordering": ["name", "id"]},
        ),
        migrations.CreateModel(
            name="ProjectModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=160)),
                ("normalized_name", models.CharField(max_length=160)),
                ("archived_at", models.DateTimeField(blank=True, null=True)),
                ("version", models.PositiveBigIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="projects.clientmodel"
                    ),
                ),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="companies.companymodel"
                    ),
                ),
                (
                    "created_by_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="identity.userprojectionmodel",
                    ),
                ),
            ],
            options={"db_table": "projects", "ordering": ["name", "id"]},
        ),
        migrations.CreateModel(
            name="ProjectAccessModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="accesses",
                        to="projects.projectmodel",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="identity.userprojectionmodel",
                    ),
                ),
            ],
            options={"db_table": "project_accesses"},
        ),
        migrations.AddConstraint(
            model_name="clientmodel",
            constraint=models.UniqueConstraint(
                fields=("company", "normalized_name"), name="uq_client_company_name"
            ),
        ),
        migrations.AddConstraint(
            model_name="projectmodel",
            constraint=models.UniqueConstraint(
                fields=("client", "normalized_name"), name="uq_project_client_name"
            ),
        ),
        migrations.AddConstraint(
            model_name="projectaccessmodel",
            constraint=models.UniqueConstraint(
                fields=("project", "user"), name="uq_project_access_user"
            ),
        ),
    ]
