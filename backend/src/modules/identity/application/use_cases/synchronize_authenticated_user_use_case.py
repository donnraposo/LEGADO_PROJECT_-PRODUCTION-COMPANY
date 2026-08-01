from modules.identity.application.dto.authenticated_identity import AuthenticatedIdentity
from modules.identity.application.ports.user_projection_repository import (
    UserProjectionRepository,
)
from modules.identity.domain.entities.user_projection import UserProjection


class SynchronizeAuthenticatedUserUseCase:
    def __init__(self, repository: UserProjectionRepository) -> None:
        self._repository = repository

    def execute(self, identity: AuthenticatedIdentity) -> UserProjection:
        return self._repository.synchronize(identity)
