class ProjectNotFoundError(Exception):
    pass


class ActiveAdministratorRequiredError(Exception):
    pass


class ClientNotFoundError(Exception):
    pass


class ClientNameConflictError(Exception):
    pass


class ProjectNameConflictError(Exception):
    pass
