from django.db import migrations, models


def populate_event_details(apps, schema_editor) -> None:
    audit_event = apps.get_model("audit", "AuditEventModel")
    presentations = {
        "COMPANY_INVITATION_CREATED": (
            "Convite criado",
            "Um convite de acesso à empresa foi criado.",
        ),
        "COMPANY_INVITATION_ACCEPTED": (
            "Convite aceito",
            "Um convite foi aceito e o vínculo empresarial foi ativado.",
        ),
        "COMPANY_INVITATION_CANCELLED": (
            "Convite cancelado",
            "Um convite pendente foi cancelado.",
        ),
        "COMPANY_MEMBERSHIP_UPDATED": (
            "Membro atualizado",
            "O papel ou estado de um membro da empresa foi alterado.",
        ),
        "PROJECT_ACCESS_GRANTED": (
            "Acesso a projeto concedido",
            "Um Administrador recebeu acesso a um projeto.",
        ),
        "PROJECT_ACCESS_REVOKED": (
            "Acesso a projeto revogado",
            "O acesso de um Administrador a um projeto foi revogado.",
        ),
    }
    for event in audit_event.objects.all().iterator():
        name, description = presentations.get(
            event.event_type,
            (event.event_type.replace("_", " ").title(), "Evento funcional registrado."),
        )
        old_state = event.old_state or {}
        new_state = event.new_state or {}
        change_state = {}
        for field in sorted(old_state.keys() | new_state.keys()):
            old_value = old_state.get(field)
            new_value = new_state.get(field)
            if old_value != new_value:
                change_state[field] = {"old": old_value, "new": new_value}
        event.action_name = name
        event.description = description
        event.change_state = change_state
        event.save(update_fields=["action_name", "description", "change_state"])


class Migration(migrations.Migration):
    dependencies = [("audit", "0001_initial")]
    operations = [
        migrations.RenameField(
            model_name="auditeventmodel",
            old_name="before",
            new_name="old_state",
        ),
        migrations.RenameField(
            model_name="auditeventmodel",
            old_name="after",
            new_name="new_state",
        ),
        migrations.AddField(
            model_name="auditeventmodel",
            name="action_name",
            field=models.CharField(default="", max_length=160),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="auditeventmodel",
            name="description",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="auditeventmodel",
            name="change_state",
            field=models.JSONField(default=dict),
        ),
        migrations.RunPython(populate_event_details, migrations.RunPython.noop),
    ]
