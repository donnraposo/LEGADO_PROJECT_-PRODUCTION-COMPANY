from abc import ABC, abstractmethod
from uuid import UUID

from legado_agent.domain.analysis_batch import AnalysisBatch
from legado_agent.domain.analysis_item import AnalysisItem


class AnalysisRepository(ABC):
    @abstractmethod
    def create_batch(self, batch: AnalysisBatch) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_batch_status(self, batch_id: UUID, status: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_item(self, item: AnalysisItem) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_items(self, batch_id: UUID) -> list[AnalysisItem]:
        raise NotImplementedError

    @abstractmethod
    def latest_batch(self, company_id: UUID, project_id: UUID) -> AnalysisBatch | None:
        raise NotImplementedError

    @abstractmethod
    def set_item_selected(self, item_id: UUID, selected: bool) -> None:
        raise NotImplementedError
