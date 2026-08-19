from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SendInvitationEmailCommand:
    email: str
    company_name: str
    token: str
    task_id: str
    attempt_number: int
