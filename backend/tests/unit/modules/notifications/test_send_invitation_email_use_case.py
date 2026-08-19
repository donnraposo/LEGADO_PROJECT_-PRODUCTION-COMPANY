from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.notifications.application.dto.send_invitation_email_command import (
    SendInvitationEmailCommand,
)
from modules.notifications.application.ports.delivery_recorder import DeliveryRecorder
from modules.notifications.application.ports.email_sender import EmailSender
from modules.notifications.application.use_cases.send_invitation_email_use_case import (
    SendInvitationEmailUseCase,
)


def test_failure_is_recorded_with_safe_error_type() -> None:
    sender = Mock(spec=EmailSender)
    recorder = Mock(spec=DeliveryRecorder)
    delivery_id = uuid4()
    recorder.start.return_value = delivery_id
    sender.send_company_invitation.side_effect = ConnectionError("sensitive details")
    command = SendInvitationEmailCommand(
        email="member@example.com",
        company_name="Legado",
        token="secret-token",
        task_id="task-1",
        attempt_number=2,
    )

    with pytest.raises(ConnectionError):
        SendInvitationEmailUseCase(sender, recorder).execute(command)

    recorder.mark_failed.assert_called_once_with(delivery_id, "ConnectionError")
    recorder.mark_delivered.assert_not_called()
