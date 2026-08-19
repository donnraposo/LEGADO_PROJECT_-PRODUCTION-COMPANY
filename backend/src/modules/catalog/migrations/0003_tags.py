import uuid

import django.db.models.deletion
from django.db import migrations, models

SYSTEM_TAGS = [
    "Bruto",
    "Selecionado",
    "Em edição",
    "Em revisão",
    "Aprovado",
    "Final",
    "Publicado",
    "Arquivado",
]


def create_system_tags(apps, schema_editor):
    tag_model = apps.get_model("catalog", "TagModel")
    tag_model.objects.bulk_create(
        [
            tag_model(name=name, normalized_name=name.casefold(), is_system=True)
            for name in SYSTEM_TAGS
        ]
    )


def remove_system_tags(apps, schema_editor):
    apps.get_model("catalog", "TagModel").objects.filter(is_system=True).delete()


class Migration(migrations.Migration):
    dependencies = [("catalog", "0002_metadataversionmodel")]

    operations = [
        migrations.CreateModel(
            name="TagModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("company_id", models.UUIDField(blank=True, db_index=True, null=True)),
                ("name", models.CharField(max_length=80)),
                ("normalized_name", models.CharField(max_length=80)),
                ("is_system", models.BooleanField(default=False)),
                ("archived_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "tags",
                "ordering": ["name", "id"],
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(("is_system", True)),
                        fields=("normalized_name",),
                        name="uq_system_tag_name",
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(("is_system", False)),
                        fields=("company_id", "normalized_name"),
                        name="uq_company_tag_name",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="MediaFileTagModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("applied_by_user_id", models.UUIDField(db_index=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "media_file",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tag_assignments",
                        to="catalog.mediafilemodel",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="media_assignments",
                        to="catalog.tagmodel",
                    ),
                ),
            ],
            options={
                "db_table": "media_file_tags",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("media_file", "tag"), name="uq_media_file_tag"
                    )
                ],
            },
        ),
        migrations.RunPython(create_system_tags, remove_system_tags),
    ]
