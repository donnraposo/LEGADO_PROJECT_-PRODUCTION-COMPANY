from uuid import UUID

from django.db import IntegrityError

from modules.projects.application.dto.client_summary import ClientSummary
from modules.projects.application.exceptions import ClientNameConflictError
from modules.projects.application.ports.client_repository import ClientRepository
from modules.projects.domain.value_objects.normalized_name import NormalizedName
from modules.projects.infrastructure.persistence.models.client_model import ClientModel


class DjangoClientRepository(ClientRepository):
    def list_active(self, company_id: UUID) -> list[ClientSummary]:
        return [
            self._summary(item)
            for item in ClientModel.objects.filter(company_id=company_id, archived_at__isnull=True)
        ]

    def create(self, company_id: UUID, name: NormalizedName) -> ClientSummary:
        try:
            item = ClientModel.objects.create(
                company_id=company_id, name=name.value, normalized_name=name.normalized
            )
        except IntegrityError as exc:
            raise ClientNameConflictError from exc
        return self._summary(item)

    @staticmethod
    def _summary(item: ClientModel) -> ClientSummary:
        return ClientSummary(item.id, item.name, item.version)
