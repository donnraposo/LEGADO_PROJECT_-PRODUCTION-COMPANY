from uuid import uuid4

import pytest
from django.test import TestCase

from modules.audit.infrastructure.persistence.models.audit_event_model import AuditEventModel


class AuditEventImmutabilityTest(TestCase):
    def test_model_rejects_update_and_delete(self) -> None:
        event = AuditEventModel.objects.create(
            company_id=uuid4(),
            actor_user_id=uuid4(),
            event_type="TEST_EVENT",
            action_name="Evento de teste",
            description="Evento criado para validar imutabilidade.",
            subject_type="test",
            subject_id=uuid4(),
        )

        event.event_type = "CHANGED"
        with pytest.raises(TypeError):
            event.save()
        with pytest.raises(TypeError):
            event.delete()

        event.refresh_from_db()
        assert event.event_type == "TEST_EVENT"
