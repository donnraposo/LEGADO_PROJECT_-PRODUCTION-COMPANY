from modules.operations.application.exceptions import InvalidAgentCommandTransitionError


class CommandTransitionPolicy:
    _TRANSITIONS = {
        "PENDING": {"ACKNOWLEDGED", "CANCELLED"},
        "ACKNOWLEDGED": {"RUNNING", "FAILED", "CANCELLED"},
        "RUNNING": {"RUNNING", "SUCCEEDED", "FAILED", "CANCELLED"},
    }

    @classmethod
    def validate(cls, current: str, desired: str) -> None:
        if desired not in cls._TRANSITIONS.get(current, set()):
            raise InvalidAgentCommandTransitionError
