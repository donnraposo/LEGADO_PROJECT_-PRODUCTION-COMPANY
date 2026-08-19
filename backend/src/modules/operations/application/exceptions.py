class MachineNotFoundError(Exception):
    pass


class CommandIdempotencyConflictError(Exception):
    pass


class AgentCommandNotFoundError(Exception):
    pass


class AgentCommandVersionConflictError(Exception):
    pass


class InvalidAgentCommandTransitionError(Exception):
    pass
