from modules.notifications.application.dto.send_invitation_email_command import (
    SendInvitationEmailCommand,
)
from modules.notifications.application.ports.delivery_recorder import DeliveryRecorder
from modules.notifications.application.ports.email_sender import EmailSender


class SendInvitationEmailUseCase:
    def __init__(self, sender: EmailSender, recorder: DeliveryRecorder) -> None:
        self._sender = sender
        self._recorder = recorder

    def execute(self, command: SendInvitationEmailCommand) -> None:
        delivery_id = self._recorder.start(command.email, command.task_id, command.attempt_number)
        try:
            self._sender.send_company_invitation(command.email, command.company_name, command.token)
        except Exception as exc:
            self._recorder.mark_failed(delivery_id, type(exc).__name__)
            raise
        self._recorder.mark_delivered(delivery_id)
