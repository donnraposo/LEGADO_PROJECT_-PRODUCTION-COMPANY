from abc import ABC, abstractmethod

from modules.identity.application.dto.authenticated_identity import AuthenticatedIdentity
from modules.identity.domain.entities.user_projection import UserProjection


class UserProjectionRepository(ABC):
    @abstractmethod
    def synchronize(self, identity: AuthenticatedIdentity) -> UserProjection:
        raise NotImplementedError
