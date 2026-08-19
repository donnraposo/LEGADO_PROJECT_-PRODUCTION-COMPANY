from uuid import UUID

from modules.catalog.application.ports.machine_catalog_authorization import (
    MachineCatalogAuthorization,
)
from modules.operations.infrastructure.persistence.models.machine_model import MachineModel


class DjangoMachineCatalogAuthorization(MachineCatalogAuthorization):
    def is_registered_to_user(self, company_id: UUID, machine_id: UUID, user_id: UUID) -> bool:
        return MachineModel.objects.filter(
            id=machine_id,
            company_id=company_id,
            registered_by_user_id=user_id,
        ).exists()
