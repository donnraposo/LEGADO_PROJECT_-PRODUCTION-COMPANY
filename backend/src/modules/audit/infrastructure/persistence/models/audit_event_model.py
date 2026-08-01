import uuid

from django.db import models


class AuditEventModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.UUIDField(db_index=True)
    actor_user_id = models.UUIDField(db_index=True)
    event_type = models.CharField(max_length=120, db_index=True)
    action_name = models.CharField(max_length=160)
    description = models.TextField()
    subject_type = models.CharField(max_length=80)
    subject_id = models.UUIDField()
    old_state = models.JSONField(null=True, blank=True)
    new_state = models.JSONField(null=True, blank=True)
    change_state = models.JSONField(default=dict)
    correlation_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    occurred_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_events"
        ordering = ["-occurred_at", "id"]

    def save(self, *args, **kwargs) -> None:
        if not self._state.adding:
            raise TypeError("Eventos de auditoria são imutáveis.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("Eventos de auditoria não podem ser excluídos.")
