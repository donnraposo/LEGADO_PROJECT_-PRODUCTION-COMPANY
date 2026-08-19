from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalog", "0003_tags")]

    operations = [
        migrations.AlterField(
            model_name="mediafilemodel",
            name="status",
            field=models.CharField(
                choices=[
                    ("DESCOBERTO", "DESCOBERTO"),
                    ("ANALISADO", "ANALISADO"),
                    ("AGUARDANDO_CONFIRMACAO", "AGUARDANDO_CONFIRMACAO"),
                    ("ORGANIZANDO", "ORGANIZANDO"),
                    ("ORGANIZADO", "ORGANIZADO"),
                    ("AGUARDANDO_UPLOAD", "AGUARDANDO_UPLOAD"),
                    ("ENVIANDO", "ENVIANDO"),
                    ("VERIFICANDO", "VERIFICANDO"),
                    ("SINCRONIZADO", "SINCRONIZADO"),
                    ("CONFLITO", "CONFLITO"),
                    ("INTERROMPIDO", "INTERROMPIDO"),
                    ("AGUARDANDO_INTERNET", "AGUARDANDO_INTERNET"),
                    ("DISPOSITIVO_DESCONECTADO", "DISPOSITIVO_DESCONECTADO"),
                    ("FALHA_DE_INTEGRIDADE", "FALHA_DE_INTEGRIDADE"),
                    ("AGUARDANDO_INTERVENCAO", "AGUARDANDO_INTERVENCAO"),
                    ("CANCELADO", "CANCELADO"),
                ],
                db_index=True,
                default="DESCOBERTO",
                max_length=40,
            ),
        ),
        migrations.AddConstraint(
            model_name="mediafilemodel",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        "DESCOBERTO",
                        "ANALISADO",
                        "AGUARDANDO_CONFIRMACAO",
                        "ORGANIZANDO",
                        "ORGANIZADO",
                        "AGUARDANDO_UPLOAD",
                        "ENVIANDO",
                        "VERIFICANDO",
                        "SINCRONIZADO",
                        "CONFLITO",
                        "INTERROMPIDO",
                        "AGUARDANDO_INTERNET",
                        "DISPOSITIVO_DESCONECTADO",
                        "FALHA_DE_INTEGRIDADE",
                        "AGUARDANDO_INTERVENCAO",
                        "CANCELADO",
                    ]
                ),
                name="ck_media_file_status",
            ),
        ),
    ]
